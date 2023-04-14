This is my writeup for [Fools2023](https://fools2023.online/index.php), a CTF created by TheZZAZZGlitch. 

This repo is an unorganised mess of code, notes, and dumps. 

This was primarily a collaboration with penteract (aka tesseract); and I also exchanged a few ideas with Buurazu.

Thanks to penteract for all the help with solving these challenges, TheZZAZZGlitch for creating this, and the GCRI discord. 

# First flags 

There are 3 servers available. Server 1, on port 13337, is the most useful for now - it provides several a console with several commands for reading and writing memory, executing code, and reading files. Server 2 (on port 13338) requires a username and password, and server 3 just contains some information. 

The primary challenges in the CTF are based around reverse engineering the unknown architecture, the GLVM, that these servers are running on; which server 3 tells us is Z80 based. My prior experience with Z80 based architectures comes from the GameBoy, which previous Fools events by TheZZAZZGlitch have been built around. 

However, before needing to do any sort of revere engineering, two flags are obtainable from just the resources available. Firstly, using the console allows us to read the files on server 1, one of which is `TODO.TXT`, which contains a 50-point flag and some helpful information. Secondly, by reading the memory, and processing the dump a bit so that ascii text can be seen, a flag can be seen nearby some text saying "Wow! Undocumented monitor command!". Printing this text through the console yields a flag that doesn't work, due to it depending on the value of certain memory locations. But scanning through the dump for the names of other commands, the two-letter commands `rf` and `ls` can be seen, also nearby the one-letter commands; and also nearby `UC` - which turns out to indeed be the undocumented command that outputs the correct flag, worth another 50 points. 

# Creating tools, and starting to reverse engineer the architecture

Quickly, repeatedly typing commands to the console to read, write, and execute memory became tedious. So I started creating [some Python code](interface.py) to interface with the server and automate these commands, and some common combinations of them (like writing some code and then immediately executing it - by far my most commonly used utility function). From that point, I could do the majority of the work in my `ipython` terminal; alongside ad-hoc code to process data. 

Now, to begin reverse-engineering, I had three sample programs to reference - the two files `MATHTEST.PRG` and `REPORT03.PRG` found from reading the files available to server 1, and the console itself. Upon hitting a breakpoint (opcode `00`), the console would print the values of the four general registers R0-R3, the program counter at the point the breakpoint was hit, the stack pointer, and the contents of the stack. The two program files each had a clear goal to crack - `REPORT03.PRG` was decrypting something, and wanted me to figure out how in order to break the encryption; and `MATHTEST.PRG` wanted me to understand enough of the architecture to write my own SQRT function. 

The first thing I did was to run each opcode in turn, and see where the breakpoint ends up at; this would tell me how many bytes worth of arguments each opcode takes; as well as which ones caused an illegal instruction to occur - either because they were illegal themselves, or they caused code execution to jump somewhere that contained illegal instructions. I then recorded all of this information in a colour-coded spreadsheet, to more easily visualise patterns in similar opcodes near each other. 

Then I started studying the programs I had access to, figuring out from context what certain opcodes might mean, and confirming them through tests. For example, there were some function names and addresses listed in `TODO.TXT`, so when I saw those addresses I suspected they were preceded by a `call` instruction. Addresses that pointed to code were probably jump instructions; and the two program files each had checks to see whether they were executing at address `$2000`, so I expected a `cmp` instruction with that argument and a conditional jump. Several instructions also come in groups that worked on each combination of registers it affected; e.g. once I'd found an immediate register load instruction (`ld R2 $XXXX`) then I would test the adjacent opcodes to confirm that they were `ld R1 $XXXX` etc. 

Once I had a few opcodes known, I started to build a [disassembler](/disasemble.py); which made it easier to see the structure of the programs and decode more opcodes. 

# Decrypting `REPORT03.PRG`

WIP