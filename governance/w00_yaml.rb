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
      raise "mapping keys must be scalars" unless key.is_a?(Psych::Nodes::Scalar)
      parsed = Psych::Visitors::ToRuby.create.accept(key)
      keys << [parsed.class.name, parsed.inspect]
    end
  end
  raise "duplicate effective YAML key" unless keys.uniq.length == keys.length
  keys
end
mappings.each { |mapping| effective.call(mapping, []) }

Psych.safe_load(stream.to_yaml, permitted_classes: [], permitted_symbols: [], aliases: true)
