# hog sources this file before it reads the list files, so running ohsh here
# keeps them in step with the manifests every time the project is created.
set repo_path $globalSettings::repo_path
set list_dir [file join [file dirname [info script]] list]

# Vivado points PYTHONHOME and PYTHONPATH at the Python it ships with,
# which stops any other Python from starting, so ohsh runs without them.
# exec treats anything on stderr as a failure, which would turn an ohsh warning
# into a failed project creation. 2>@1 leaves that to the exit code.
puts [exec env -u PYTHONHOME -u PYTHONPATH \
    ohsh --format hog -t $repo_path/projects/simple -o $list_dir \
    --relative-to $repo_path -w demo_lib accumulator 2>@1]
