# mpc-plugin-optimize

A Claude skill for making Akai MPC plugins cheaper on the CPU of the 32-bit standalone models: MPC X,
Live, Live II, One, One+, Key 61, Key 37 and Force.

Those models run plugins on an ARM Cortex-A17 at 1.6 GHz. Code that is comfortable on a laptop can
cause dropouts there. This skill gives Claude a measured method for a plugin built with the MPC Plugin
SDK: count what the code costs, find where the cost is, change one thing, prove the sound did not
change, and count again.

## What is inside

| File | Contents |
|---|---|
| `skills/mpc-plugin-optimize/SKILL.md` | The method: what to ask first, the measuring loop, when to stop |
| `skills/mpc-plugin-optimize/reference.md` | The guide: cycle costs timed on an MPC One+, compiler behavior, cache budget, NEON rules, bench behavior. Every figure is tagged with where it came from |
| `skills/mpc-plugin-optimize/scripts/count.sh` | Counts the instructions each audio block executes, for the 32-bit ARM build under an emulator |
| `skills/mpc-plugin-optimize/scripts/scan.sh` | Compiles to 32-bit ARM assembly and counts the costly patterns per function |
| `skills/mpc-plugin-optimize/scripts/drive.cpp` | The small host program both scripts use; on a device it is also a random-parameter CPU bench |
| `skills/mpc-plugin-optimize/scripts/openmpc-bench.sh` | Fetches the current CPU bench of the [Open MPC](https://github.com/open-mpc/mpc-vst-plugins) plugin catalog, builds it and runs it on your MPC, for the verdict that catalog uses |

The reference is useful by itself as reading for anyone who writes DSP for these machines.

## Install

**Claude Code, as a plugin**

```
/plugin marketplace add anthonytheinventor/mpc-plugin-optimize
/plugin install mpc-plugin-optimize@anthonytheinventor-mpc
```

**Claude Code, by copying**

Copy the folder `skills/mpc-plugin-optimize` into `~/.claude/skills/` for every project, or into
`.claude/skills/` of one project. In a checkout of the MPC Plugin SDK it then sits beside the SDK's
own skills.

**Claude apps**

Download `mpc-plugin-optimize.zip` from the latest release and upload it under Settings, Capabilities,
Skills.

## Use

Ask in plain words, in a session that has your plugin project open:

- "My plugin drops out at 32-frame blocks. Find out why."
- "Cut the CPU of this effect without changing its sound."
- "This plugin fails the CPU bench on the worst block."

Claude loads the skill when the request matches. In Claude Code you can also call it by name:
`/mpc-plugin-optimize:mpc-plugin-optimize` when installed as a plugin, `/mpc-plugin-optimize` when
copied.

## What the scripts need

A Linux shell (WSL on Windows) with `zig`, `qemu-arm` 8.1 or later, `nm`, `awk` and `c++filt`, and a
checkout of the MPC Plugin SDK. The Open MPC bench also needs `curl`, `ssh` and `scp`, and an MPC with
developer mode on.

```
scripts/count.sh <sdk-dir> <plugin.cpp>          # steady state
scripts/count.sh <sdk-dir> <plugin.cpp> 4        # four random parameters per block
scripts/scan.sh  <sdk-dir> <plugin.cpp>
scripts/openmpc-bench.sh <plugin-arm32.so> <mpc-ip> -p     # Open MPC's bench, on the device
```

## License

MIT. See [LICENSE](LICENSE).
