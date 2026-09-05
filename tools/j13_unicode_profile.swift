import Foundation

// Bounded operations from Biblos d486b5cd428b21602637777d2f3bc89488146e4f.
struct Item: Decodable {
  let text: String
  let plainText: Bool
  let endpoints: [Int]
}
struct Request: Decodable { let items: [Item] }
struct Result: Encodable {
  let plainTextError: String?
  let scalarCount: Int
  let endpointErrors: [String?]
  enum CodingKeys: CodingKey { case plainTextError, scalarCount, endpointErrors }
  func encode(to encoder: Encoder) throws {
    var container = encoder.container(keyedBy: CodingKeys.self)
    try container.encode(plainTextError, forKey: .plainTextError)
    try container.encode(scalarCount, forKey: .scalarCount)
    try container.encode(endpointErrors, forKey: .endpointErrors)
  }
}
let patterns = [
    "^#{1,6}(?:[ ]+|$)",
    "^>",
    "^[-*+][ ]+",
    "^[0-9]{1,9}[.)][ ]+",
    "^(?:\\*[ ]*){3,}$",
    "^(?:-[ ]*){3,}$",
    "^(?:_[ ]*){3,}$",
    "(?<!\\*)\\*\\*\\*(?![[:space:]\\*])[^\\r\\n]*?[^[:space:]\\*]\\*\\*\\*(?!\\*)",
    "(?<!\\*)\\*\\*(?![[:space:]\\*])[^\\r\\n]*?[^[:space:]\\*]\\*\\*(?!\\*)",
    "(?<!\\*)\\*(?![[:space:]\\*])[^\\r\\n\\*]*?[^[:space:]\\*]\\*(?!\\*)",
    "(?<![[:alnum:]_])___(?![[:space:]_])[^\\r\\n]*?[^[:space:]_]___(?![[:alnum:]_])",
    "(?<![[:alnum:]_])__(?![[:space:]_])[^\\r\\n]*?[^[:space:]_]__(?![[:alnum:]_])",
    "(?<![[:alnum:]_])_(?![[:space:]_])[^\\r\\n_]*?[^[:space:]_]_(?![[:alnum:]_])",
    "(?<!~)~~(?![[:space:]~])[^\\r\\n]*?[^[:space:]~]~~(?!~)",
    "^\\[[^\\]\\r\\n]+\\]:[ ]*\\S+",
    "<[A-Za-z][A-Za-z0-9+.-]*:[^<>[:space:]]+>",
    "<[^<>[:space:]@]+@[^<>[:space:]@]+>",
    "<!--[\\s\\S]*?-->",
    "<![[:alpha:]][^>]*>",
    "<\\?[^>]*\\?>",
    "</?[[:alpha:]][^>]*>",
    "!?\\[[^\\]]*\\]\\([^\\)]*\\)",
    "!?\\[[^\\]]+\\]\\[[^\\]]*\\]",
    "`[^`]+`",
    "```",
    "~~~",
    "(?<![A-Za-z0-9+.-])(?:mailto:|data:|file:|tel:|sms:|javascript:|www\\.)[^[:space:]]*",
    "[A-Za-z][A-Za-z0-9+.-]*://[^[:space:]]*",
]

func plainTextError(_ value: String) -> String? {
  guard !value.isEmpty,
    value == value.trimmingCharacters(in: .whitespacesAndNewlines)
  else { return "proseViolation" }
  guard !value.unicodeScalars.contains(where: {
    $0.value <= 0x1F || (0x7F...0x9F).contains($0.value)
  }) else { return "markupViolation" }
  if patterns.contains(where: {
    value.range(of: $0, options: [.regularExpression, .caseInsensitive]) != nil
  }) { return "markupViolation" }
  return nil
}

func endpointError(_ offset: Int, _ value: String) -> String? {
  let units = value.utf16
  guard offset >= 0, offset <= units.count else { return "invalidUTF16Range" }
  if offset > 0, offset < units.count {
    let prior = units[units.index(units.startIndex, offsetBy: offset - 1)]
    let current = units[units.index(units.startIndex, offsetBy: offset)]
    guard !(0xD800...0xDBFF).contains(prior), !(0xDC00...0xDFFF).contains(current)
    else { return "invalidStringBoundary" }
  }
  let boundaries = Set(value.indices.map {
    units.distance(from: units.startIndex, to: $0.samePosition(in: units)!)
  } + [units.count])
  guard boundaries.contains(offset) else { return "graphemeSplit" }
  guard let index = units.index(units.startIndex, offsetBy: offset, limitedBy: units.endIndex),
    String.Index(index, within: value) != nil
  else { return "invalidStringBoundary" }
  return nil
}

let request = try JSONDecoder().decode(Request.self, from: FileHandle.standardInput.readDataToEndOfFile())
let results = request.items.map { item in
  Result(plainTextError: item.plainText ? plainTextError(item.text) : nil,
         scalarCount: item.text.unicodeScalars.count,
         endpointErrors: item.endpoints.map { endpointError($0, item.text) })
}
FileHandle.standardOutput.write(try JSONEncoder().encode(results))
