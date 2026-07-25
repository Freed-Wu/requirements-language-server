if $cursor[1] == 0 or $nodes[0].type == "option" | not then
  empty
end | to_entries[] |
if .key | gsub("="; "") | ($nodes[0].text as $text | if $complete then startswith($text) else . == $text end) then
  {
    label: .key,
    insert_text: .key,
    kind: $enums.CompletionItemKind.Function,
    documentation: {kind: "plaintext", value: .value}
  }
else
  empty
end
