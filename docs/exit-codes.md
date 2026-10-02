# Exit codes

ohsh follows the Unix conventions where one exists (`1`, `2`, and the BSD
`sysexits.h` codes 64 to 78). Errors specific to ohsh start at 100.

| Code | Meaning                                                        |
|------|----------------------------------------------------------------|
| 0    | Success.                                                       |
| 1    | Unexpected error.                                              |
| 2    | Invalid command-line arguments.                                |
| 65   | A manifest is not valid JSON or has the wrong structure.       |
| 66   | Top directory, manifest or source file missing or unreadable.  |
| 73   | Output directory cannot be created.                            |
| 100  | Top module not found in any manifest.                          |
| 101  | A dependency has no manifest.                                  |
| 102  | Modules depend on each other in a loop.                        |
| 103  | A module name is declared in more than one manifest.           |
