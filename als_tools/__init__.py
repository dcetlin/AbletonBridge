"""Edit Live sets (.als) directly, for changes the Live Object Model can't make,
such as copying Max for Live parameter mappings between sets.

- `als_tools.clone`: copy mapped tracks and devices, and rack-macro automation
  (`als-clone`)
- `als_tools.validate`: structural checks (`als-validate`)
- `als_tools.trace`: follow each macro from source to OSC address (`als-trace`)
- `als_tools.spec`: the typed spec that `als-clone` accepts
- `als_tools.liveset`: XML access and id handling shared by the others
"""
