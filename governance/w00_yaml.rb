require "psych"

stream = Psych.parse_stream(STDIN.read)
raise "one YAML document is required" unless stream.children.length == 1

root = stream.children.first.root
anchors, mappings, aliases = {}, [], 0

visit = lambda do |node, depth|
  raise "YAML nesting is excessive" if depth > 20
  anchor = node.anchor unless node.is_a?(Psych::Nodes::Alias)
  if anchor
    raise "duplicate YAML anchor" if anchors.key?(anchor)
    anchors[anchor] = node
  end
  aliases += 1 if node.is_a?(Psych::Nodes::Alias)
  mappings << node if node.is_a?(Psych::Nodes::Mapping)
  raise "too many YAML aliases" if aliases > 32
  Array(node.children).each { |child| visit.call(child, depth + 1) }
end
visit.call(root, 0)

acyclic = nil
acyclic = lambda do |node, stack|
  target = node.is_a?(Psych::Nodes::Alias) ? anchors.fetch(node.anchor) : node
  raise "cyclic YAML alias" if stack.include?(target.object_id)
  Array(target.children).each { |child| acyclic.call(child, [*stack, target.object_id]) }
end
acyclic.call(root, [])

key_id = lambda do |node|
  raise "mapping keys must be scalars" unless node.is_a?(Psych::Nodes::Scalar)
  value = Psych::Visitors::ToRuby.create.accept(node)
  [value.class.name, value.inspect]
end

effective = nil
effective = lambda do |mapping, stack|
  raise "invalid YAML merge target" unless mapping.is_a?(Psych::Nodes::Mapping) && !stack.include?(mapping.object_id)
  keys = []
  mapping.children.each_slice(2) do |key, value|
    if key.value == "<<"
      sources = value.is_a?(Psych::Nodes::Sequence) ? value.children : [value]
      sources.each do |source|
        target = source.is_a?(Psych::Nodes::Alias) ? anchors.fetch(source.anchor) : source
        keys.concat(effective.call(target, [*stack, mapping.object_id]))
      end
    else
      keys << key_id.call(key)
    end
  end
  raise "duplicate effective YAML key" unless keys.uniq.length == keys.length
  keys
end
mappings.each { |mapping| effective.call(mapping, []) }

document = Psych.safe_load(stream.to_yaml, permitted_classes: [], permitted_symbols: [], aliases: true)
if ARGV == ["workflow"]
  jobs = document["jobs"] if document.is_a?(Hash)
  raise "workflow must define exactly two jobs" unless jobs.is_a?(Hash) && jobs.length == 2
  names = jobs.map do |identifier, job|
    raise "workflow job must be a mapping" unless job.is_a?(Hash)
    (job["name"] || identifier).to_s.strip.downcase.gsub(/\s+/, " ")
  end
  raise "workflow check names differ" unless names.uniq.length == 2 && names.sort == ["project-integrity", "turn-handoff-integrity"]
end
