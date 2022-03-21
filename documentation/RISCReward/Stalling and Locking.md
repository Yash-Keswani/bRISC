To prevent RAW and WAW hazards, a stalling mechanism is used. This is performed via Stalling

### Stalling
-> A storage resource (register / memory location) is marked as in-use during the D phase, if the resource is one of the destinations of the instruction
-> If another line attempts to read from or write into that resource, then the execution of that line is stalled
-> The 'cycling' of instructions is paused until the lock is released
-> Locks are released during the M phase for memory writes, and the W phase for register bytes
-> If a speculated instruction is clobbered during branching (during the X phase), any locks held by it are released as well

### Locking
-> While I am calling this a lock, the implementation of this lock is closer to a semaphore
-> An integer containing the number of writers holding onto this lock is kept
-> When the lock is held, the count raises by 1. When a lock is released, the count falls by 1
-> Any attempt to release an already-released lock have no consequence. This has mostly been necessary due to the FLAGS register, but may change in the future
-> Locks are implemented via a dict, that contains an entry for each register. Entries for memory locations do not exist at the beginning, but will be filled up as locks are acquired. Note that these locks are not deleted when released
