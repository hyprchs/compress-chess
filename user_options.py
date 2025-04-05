from enum import StrEnum


class MoveEncodingOption(StrEnum):
    from_uci = 'from_uci'
    """
    Encode using the naive approach, using 12 bits per move: 6 for the move's
    ``from_square`` and 6 for its ``to_square``.
    """

    huffman_code_uci = 'huffman_code_uci'
    """
    Encode moves with a Huffman code based on the UCI string of all moves in the game.
    """

    huffman_code_san = 'huffman_code_san'
    """
    Encode moves with a Huffman code based on the SAN string of all moves in the game.
    """

    map_to_action_space = 'map_to_action_space'
    """
    Map the move to an 11-bit representation based on chess's 
    `discrete action space <https://www.google.com>`_ of size 1924.
    """

    map_to_action_space_2fold_symmetry = 'map_to_action_space_2fold_symmetry'
    """
    Map moves that are symmetric about 4th/5th rank line to a 10-bit 
    representation, assuming the corresponding symmetric move is impossible, 
    based on chess's `discrete action space <https://www.google.com>`_. 
    Fall back to the 11-bit representation if both moves are possible.
    """

    map_to_action_space_4fold_symmetry = 'map_to_action_space_4fold_symmetry'
    """
    Map moves that are symmetric about the 4th/5th rank line or the d/e file line
    to a 9-bit representation, assuming all corresponding symmetric moves are impossible,
    based on chess's `discrete action space <https://www.google.com>`_.
    Fall back to the 10-bit representation, or the 9-bit representation if another 
    symmetric move is possible.
    """

    '''
    TODO: After lots of unexpected roadblocks, I'm abandoning this idea for now. The number of 8-bit representations 
          necessary turns out to be 260, just over 256. It's because moves on the long diagonal must be assigned an
          8-bit binary prefix, but then do not make full use of the subsequent 3 bits, since they only have 4 moves
          in their symmetry group instead of 8. This means we run out of 8-bit prefixes too early, counterintuitively.
          Here's the math:
          
            - There are `1924` actions total (see my chess-action-space repo). This counts every
              (from_sq, to_sq) pair that would be a legal move for either a queen or a knight, and
              assigns `132 = (8 + 7 + 7) * 3 pieces * 2 colors` to underpromotions, meaning they are considered
              distinct moves from their corresponding queen promotions.
            - Moves on either long diagonal have only 4 moves in their symmetry group—there are 
              `112 = 8 * 7 * 2` of these. We need `28 = 112 / 4` 8-bit base numbers to represent them.
            - The total underpromotion action space is `132 = (8 + 7 + 7) moves * 2 sides * 3 pieces`. Again, this number
              considers underpromotions to be separate actions from their corresponding non-underpromotion moves with the same
              (from_sq, to_sq) pair. This is desirable because then we are not forced to write and consume another bit
              when encoding/decoding every move that is a promotion to distinguish an underpromotion from a much more common
              queen promotion. Additionally, by checking the turn while encoding/decoding, we can effectively reduce
              this space by half to `66 = 132 / 2`. This means we should conceptualize underpromotion moves as having only
              a single left-right symmetry axis—the diagonal symmetry axis would map the space to (from_sq, to_sq) pairs
              that are either on the left/right sides of the board where pawns can't promote, or map the pair to itself in the
              case of an underpromotion on the long diagonal of the axis; and the up-down symmetry axis would be redundant
              when we already know the turn by tracking the board state, since one color's pawns can only promote in one direction.
              Therefore, underpromotions only need to consume `11 = (8 + 7 + 7) / 2 symmetries` 8-bit bases. The running total
              for the number of 8-bit bases is now `39 = 28 long-diag moves + 11 underpromotions`.
            - All other moves of the 1924 total action space must have 8 moves in their symmetry group. There are 
              `1680 = 1924 - 112 long-diag moves - 132 underpromotions` of these moves, so we need `210 = 1680 / 8` 8-bit bases
              to represent them. The final total is `249 = 210 eight-fold moves + 28 long-diag moves + 11 underpromotions`,
              which is conveniently just under the maximum number of numbers representable in 8 bits, `256 = 2 ** 8`.
    '''
    # map_to_action_space_8fold_symmetry = 'map_to_action_space_8fold_symmetry'
    # """
    # Map moves that are symmetric about the 4th/5th rank line, the d/e file line,
    # and the a1-h8 diagonal to an 8-bit representation, assuming all corresponding
    # symmetric moves are impossible, based on chess's `discrete action space
    # <https://www.google.com>`_. Fall back to the 9-bit, 10-bit, or 11-bit representation
    # if another symmetric move is possible.
    # """

    handle_from_to_squares_separately = 'handle_from_to_squares_separately'
    """
    Provide additional options to encode ``from_square`` and ``to_square`` separately.
    """


class FromSquareEncodingOption(StrEnum):
    occupied_index = 'occupied_index'
    """
    Encode ``move.from_square`` based on its index out of the 
    truthy bits in ``board.occupied_co[board.turn()]``.
    """

    mask_legal = 'mask_legal'
    """
    Encode ``move.from_square`` based on its index out of truthy bits in the 
    bitboard that unions all of ``chess.BB_SQUARES[m.from_square]``
    for legal moves ``m`` on the board.
    """

    mask_pseudo_legal = 'mask_pseudo_legal'
    """
    Encode ``move.from_square`` based on its index out of truthy bits in the
    bitboard that unions all of ``chess.BB_SQUARES[move.from_square]``
    for pseudo-legal moves ``m`` on the board. Significantly faster than
    the ``mask_legal`` option, with slightly worse bit-savings.
    """

    square_index = 'square_index'
    """
    Encode ``move.from_square`` as a ``0–63`` integer using 6 bits. 
    """


class ToSquareEncodingOption(StrEnum):
    mask_piece_square_action_space = 'mask_potential_legal'
    """
    Encode ``move.to_square`` using a pre-generated bitboard with truthy bits
    for all squares that are potential legal moves or captures for the piece at
    ``from_square``.
    """

    mask_legal = 'mask_legal'
    """
    Encode ``move.to_square`` based on its index out of truthy bits in the
    bitboard that unions all of ``chess.BB_SQUARES[move.to_square]``
    for legal moves ``m`` on the board.
    """

    mask_pseudo_legal = 'mask_pseudo_legal'
    """
    Encode ``move.to_square`` based on its index out of truthy bits in the
    bitboard that unions all of ``chess.BB_SQUARES[move.to_square]``
    for pseudo-legal moves ``m`` on the board. Significantly faster than
    the ``mask_legal`` option, with slightly worse bit-savings.
    """
