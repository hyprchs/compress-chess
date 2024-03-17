# `compress-chess`
A Python library to turn a series of chess moves in a PGN into a small bitstring for efficient long-term storage. It has good bones, but it's a 
long-term WIP (read: might never be updated)!

# Compression specification
In general, below is the output format of a compressed PGN. Bits would be read left-to-right, top-to-bottom.

![Test](https://github.com/jacksonthall22/compress-chess/blob/main/compression-spec.png)
