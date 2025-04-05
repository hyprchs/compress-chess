# `bitPGN`

An all-in-one tool to compress and decompress PGN files for long-term storage

## Introduction
The PGN file format stores data about a chess game as plain text, including a list of headers and a list of moves in
[Standard Algebraic Notation (SAN)](https://en.wikipedia.org/wiki/Algebraic_notation_(chess)). While this
standardization makes chess games easy to view and work with, it is not space-efficient. Consider that for a 60-move
game, 171 characters are stored simply to number the moves (`1.`, `2.`, ...).

With this in mind, the goals of this library are the following:
1. Provide an all-in-one tool to compress and decompress PGN files for long-term storage, with various tradeoffs
between speed and compression ratio
2. Take advantage of chess's board symmetries and [surprisingly small action space](https://ai.stackexchange
.com/a/34733/53149) to encode moves in PGNs with maximum bit-efficiency
3. Optimize the heck out of the compression/decompression pipeline so it's feasible to use with huge game databases

## PGN Compression Strategies

### Headers
For now, this library only offers a single strategy for compressing headers. If someone is interested in contributing
to this library, they may want to start here.

The strategy is as follows. We first define a list of common PGN headers found in the
[original PGN specification](),
Lichess and Chess.com exports, popular online databases, etc.). Currently, this library
uses 28 common headers (`Event`, `Site`, `Date`, `Round`, etc)

### Moves
There are several ways we can consider representing chess moves. The options below are in increasing order of
compression ratio and decreasing order of compression/decompression speed:
- **(12 bits):** From the UCI representation (ex. `e2e4`): encode the start and end squares with 6 bits each (`1-64`).
  We can basically call this the naive approach.
- **(11 bits):** Map moves directly to chess's discrete action space, 
- [which has size 1924](https://ai.stackexchange.com/a/34733/53149) (Note that $`log_2(1924) ≈  10.91`$)
- **(8–11 bits):** Denote a move's piece's start square with 6 bits (`1-64`). The most squares any piece can 
  ever move to is 27 (ex. a queen on `d4`), and each square's position on the chess board can be mapped to one of 10 
  symmetry classes. Using this knowledge, we can hard-code a mapping to its destination square based on its symmetry
  class with at most 5 bits (for queens) and as little as two bits (for pawns, which at most could have two forward 
  and two diagonal movements). Note that this will be slower than other methods because it requires an additional 
  check about which piece moved to encode and decode its destination square.
- **(6–11 bits):** Like the last method, but check the legal moves of the move's piece to use as few bits as 
  possible for the destination square while encoding. While decoding, we have to track the game state, push 
  moves, and preform the same check for legal moves to determine how many bits should be consumed after the bits 
  denoting the start square.
- **(3—8 bits):** Assuming the standard variant, consider that the maximum number of pieces a side can have is 16 to 
  represent the start square in 4 bits, and represent the end square as in the above method.

## Bit Descriptions
We will refer to bits by their 0-indexed position.

### Bits [0, 2)

```markdown
idx:    01
      0b00
        │└╴Is the initial FEN the starting position?
        └╴Is this game a variant?
```

If bit 1 is `1`, indicating we are not in a



