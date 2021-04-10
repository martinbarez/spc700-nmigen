# SPC-700 CPU written in nMigen
## What is the SPC-700?
The sound chip found in the SNES. [snesmusic.org has a nice intro about it.](http://snesmusic.org/files/spc700.html)

## Why?
* I've never written a CPU before
* I want to learn nMigen and formal verification

## How am I doing it?
[n6800](https://github.com/RobertBaruch/n6800) is an awesome video tutorial from [Robert Baruch](https://github.com/RobertBaruch/) where he implements a 6800 CPU in nMigen. I've taken the formal verification framework, adapted it and started building my own core.

Regarding [nMigen](https://github.com/nmigen/nmigen), documentation is still a bit lacking but the language is so easy to use it has not been a problem at all. Some things are not yet finalized so I'll try to keep hacky code to a minimum.

### TODO

- [x] Formal verification framework
- [ ] Implement the ALU
- [ ] Implement all instructions (4/256)
- [ ] Connect the RAM
- [ ] Implement the DSP

### Head over to the repo's wiki if you want to see more detailed info and progress