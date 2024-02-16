(
 (global_opt (option) @_option (path) @file)
 (#match? @_option "^-(r|c|-(requirement|constraint))$")
)

(
 (global_opt (option) @_option (path) @dir)
 (#match? @_option "^-(e|-editable)$")
)
