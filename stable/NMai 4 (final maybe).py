# Skeleton Program code for the AQA A Level Paper 1 Summer 2021 examination
# this code should be used in conjunction with the Preliminary Material
# written by the AQA Programmer Team
# developed in the Python 3.5 programming environment


# !!! requires access to P2's class as well

import random
import os
from typing import Dict, List, NewType, Optional, Tuple
from fractions import Fraction
from random import choice
from threading import Timer


class Piece:
    def __init__(self, Player1):
        self._FuelCostOfMove = 1
        self._BelongsToPlayer1 = Player1
        self._Destroyed = False
        self._PieceType = "S"
        self._VPValue = 1
        self._ConnectionsToDestroy = 2

    def GetVPs(self):
        return self._VPValue

    def GetBelongsToPlayer1(self):
        return self._BelongsToPlayer1

    def CheckMoveIsValid(self, DistanceBetweenTiles, StartTerrain, EndTerrain):
        if DistanceBetweenTiles == 1:
            if StartTerrain == "~" or EndTerrain == "~":
                return self._FuelCostOfMove * 2
            else:
                return self._FuelCostOfMove
        return -1

    def HasMethod(self, MethodName):
        return callable(getattr(self, MethodName, None))

    def GetConnectionsNeededToDestroy(self):
        return self._ConnectionsToDestroy

    def GetPieceType(self):
        if self._BelongsToPlayer1:
            return self._PieceType
        else:
            return self._PieceType.lower()

    def DestroyPiece(self):
        self._Destroyed = True


class BaronPiece(Piece):
    def __init__(self, Player1):
        super(BaronPiece, self).__init__(Player1)
        self._PieceType = "B"
        self._VPValue = 10

    def CheckMoveIsValid(self, DistanceBetweenTiles, StartTerrain, EndTerrain):
        if DistanceBetweenTiles == 1:
            return self._FuelCostOfMove
        return -1


class LESSPiece(Piece):
    def __init__(self, Player1):
        super(LESSPiece, self).__init__(Player1)
        self._PieceType = "L"
        self._VPValue = 3

    def CheckMoveIsValid(self, DistanceBetweenTiles, StartTerrain, EndTerrain):
        if DistanceBetweenTiles == 1 and StartTerrain != "#":
            if StartTerrain == "~" or EndTerrain == "~":
                return self._FuelCostOfMove * 2
            else:
                return self._FuelCostOfMove
        return -1

    def Saw(self, Terrain):
        if Terrain != "#":
            return 0
        return 1


class PBDSPiece(Piece):
    def __init__(self, Player1):
        super(PBDSPiece, self).__init__(Player1)
        self._PieceType = "P"
        self._VPValue = 2
        self._FuelCostOfMove = 2

    def CheckMoveIsValid(self, DistanceBetweenTiles, StartTerrain, EndTerrain):
        if DistanceBetweenTiles != 1 or StartTerrain == "~":
            return -1
        return self._FuelCostOfMove

    def Dig(self, Terrain):
        if Terrain != "~":
            return 0
        if random.random() < 0.9:
            return 1
        else:
            return 5


class Tile:
    def __init__(self, xcoord, ycoord, zcoord, gridSize):
        self._x = xcoord
        self._y = ycoord
        self._z = zcoord
        self._Terrain = " "
        self._PieceInTile = None
        self._Neighbours = []
        self._id = (gridSize * (self._z - self._y) + self._x) // 2

    def GetDistanceToTileT(self, T):
        return max(
            max(abs(self.Getx() - T.Getx()), abs(self.Gety() - T.Gety())),
            abs(self.Getz() - T.Getz()),
        )

    def AddToNeighbours(self, N):
        self._Neighbours.append(N)

    def GetNeighbours(self):
        return self._Neighbours

    def SetPiece(self, ThePiece):
        self._PieceInTile = ThePiece

    def SetTerrain(self, T):
        self._Terrain = T

    def Getx(self):
        return self._x

    def Gety(self):
        return self._y

    def Getz(self):
        return self._z

    def GetId(self):
        return self._id

    def GetTerrain(self):
        return self._Terrain

    def GetPieceInTile(self):
        return self._PieceInTile

    def __repr__(self):
        position = "({0}, {1}, {2})".format(self._x, self._y, self._z)
        id = (8 * (self._z - self._y) + self._x) // 2
        neighbours = "Neighbours: " + ",".join(
            map(lambda x: str(x.GetId()), self._Neighbours)
        )
        if self._PieceInTile:
            return (
                "Tile "
                + str(id)
                + ", position "
                + position
                + ". "
                + neighbours
                + ", occupied by "
                + self._PieceInTile.GetPieceType()
                + "\n"
            )
        else:
            return (
                "Tile "
                + str(id)
                + ", position "
                + position
                + ". "
                + neighbours
                + ", free\n"
            )


class HexGrid:
    def __init__(self, n):
        self._Size = n
        self._Player1Turn = True
        self._Tiles = []
        self._Pieces = []
        self.__ListPositionOfTile = 0
        self.__SetUpTiles()
        self.__SetUpNeighbours()

    def GetTiles(self):
        # Note that this returns a reference to self._Tiles, which means
        # it can be used to mutate the individual Tile instances.
        # It would be better design to return a "deep copy" of the tile list
        # here, but I didn't want to change the code too much.
        # Just don't modify the tiles in your AI, please.
        return self._Tiles

    def SetUpGridTerrain(self, ListOfTerrain):
        for Count in range(0, len(ListOfTerrain)):
            self._Tiles[Count].SetTerrain(ListOfTerrain[Count])

    def AddPiece(self, BelongsToPlayer1, TypeOfPiece, Location):
        if TypeOfPiece == "Baron":
            NewPiece = BaronPiece(BelongsToPlayer1)
        elif TypeOfPiece == "LESS":
            NewPiece = LESSPiece(BelongsToPlayer1)
        elif TypeOfPiece == "PBDS":
            NewPiece = PBDSPiece(BelongsToPlayer1)
        else:
            NewPiece = Piece(BelongsToPlayer1)
        self._Pieces.append(NewPiece)
        self._Tiles[Location].SetPiece(NewPiece)

    def ExecuteCommand(self, Items, FuelAvailable, LumberAvailable, PiecesInSupply):
        FuelChange = 0
        LumberChange = 0
        SupplyChange = 0
        if Items[0] == "move":
            FuelCost = self.__ExecuteMoveCommand(Items, FuelAvailable)
            if FuelCost < 0:
                return "That move can't be done", FuelChange, LumberChange, SupplyChange
            FuelChange = -FuelCost
        elif Items[0] in ["saw", "dig"]:
            Success, FuelChange, LumberChange = self.__ExecuteCommandInTile(Items)
            if not Success:
                return "Couldn't do that", FuelChange, LumberChange, SupplyChange
        elif Items[0] == "spawn":
            LumberCost = self.__ExecuteSpawnCommand(
                Items, LumberAvailable, PiecesInSupply
            )
            if LumberCost < 0:
                return "Spawning did not occur", FuelChange, LumberChange, SupplyChange
            LumberChange = -LumberCost
            SupplyChange = 1
        elif Items[0] == "upgrade":
            LumberCost = self.__ExecuteUpgradeCommand(Items, LumberAvailable)
            if LumberCost < 0:
                return "Upgrade not possible", FuelChange, LumberChange, SupplyChange
            LumberChange = -LumberCost
        return "Command executed", FuelChange, LumberChange, SupplyChange

    def __CheckTileIndexIsValid(self, TileToCheck):
        return TileToCheck >= 0 and TileToCheck < len(self._Tiles)

    def __CheckPieceAndTileAreValid(self, TileToUse):
        if self.__CheckTileIndexIsValid(TileToUse):
            ThePiece = self._Tiles[TileToUse].GetPieceInTile()
            if ThePiece is not None:
                if ThePiece.GetBelongsToPlayer1() == self._Player1Turn:
                    return True
        return False

    def __ExecuteCommandInTile(self, Items):
        TileToUse = int(Items[1])
        Fuel = 0
        Lumber = 0
        if self.__CheckPieceAndTileAreValid(TileToUse) == False:
            return False, Fuel, Lumber
        ThePiece = self._Tiles[TileToUse].GetPieceInTile()
        Items[0] = Items[0][0].upper() + Items[0][1:]
        if ThePiece.HasMethod(Items[0]):
            Method = getattr(ThePiece, Items[0], None)
            if Items[0] == "Saw":
                Lumber += Method(self._Tiles[TileToUse].GetTerrain())
            elif Items[0] == "Dig":
                Fuel += Method(self._Tiles[TileToUse].GetTerrain())
                if abs(Fuel) > 2:
                    self._Tiles[TileToUse].SetTerrain(" ")
            return True, Fuel, Lumber
        return False, Fuel, Lumber

    def __ExecuteMoveCommand(self, Items, FuelAvailable):
        StartID = int(Items[1])
        EndID = int(Items[2])
        if not self.__CheckPieceAndTileAreValid(
            StartID
        ) or not self.__CheckTileIndexIsValid(EndID):
            return -1
        ThePiece = self._Tiles[StartID].GetPieceInTile()
        if self._Tiles[EndID].GetPieceInTile() is not None:
            return -1
        Distance = self._Tiles[StartID].GetDistanceToTileT(self._Tiles[EndID])
        FuelCost = ThePiece.CheckMoveIsValid(
            Distance, self._Tiles[StartID].GetTerrain(), self._Tiles[EndID].GetTerrain()
        )
        if FuelCost == -1 or FuelAvailable < FuelCost:
            return -1
        self.__MovePiece(EndID, StartID)
        return FuelCost

    def __ExecuteSpawnCommand(self, Items, LumberAvailable, PiecesInSupply):
        TileToUse = int(Items[1])
        if (
            PiecesInSupply < 1
            or LumberAvailable < 3
            or not self.__CheckTileIndexIsValid(TileToUse)
        ):
            return -1
        ThePiece = self._Tiles[TileToUse].GetPieceInTile()
        if ThePiece is not None:
            return -1
        OwnBaronIsNeighbour = False
        ListOfNeighbours = self._Tiles[TileToUse].GetNeighbours()
        for N in ListOfNeighbours:
            ThePiece = N.GetPieceInTile()
            if ThePiece is not None:
                if (
                    self._Player1Turn
                    and ThePiece.GetPieceType() == "B"
                    or not self._Player1Turn
                    and ThePiece.GetPieceType() == "b"
                ):
                    OwnBaronIsNeighbour = True
                    break
        if not OwnBaronIsNeighbour:
            return -1
        NewPiece = Piece(self._Player1Turn)
        self._Pieces.append(NewPiece)
        self._Tiles[TileToUse].SetPiece(NewPiece)
        return 3

    def __ExecuteUpgradeCommand(self, Items, LumberAvailable):
        TileToUse = int(Items[2])
        if (
            not self.__CheckPieceAndTileAreValid(TileToUse)
            or LumberAvailable < 5
            or not (Items[1] == "pbds" or Items[1] == "less")
        ):
            return -1
        else:
            ThePiece = self._Tiles[TileToUse].GetPieceInTile()
            if ThePiece.GetPieceType().upper() != "S":
                return -1
            ThePiece.DestroyPiece()
            if Items[1] == "pbds":
                ThePiece = PBDSPiece(self._Player1Turn)
            else:
                ThePiece = LESSPiece(self._Player1Turn)
            self._Pieces.append(ThePiece)
            self._Tiles[TileToUse].SetPiece(ThePiece)
            return 5

    def __SetUpTiles(self):
        EvenStartY = 0
        EvenStartZ = 0
        OddStartZ = 0
        OddStartY = -1
        for count in range(1, self._Size // 2 + 1):
            y = EvenStartY
            z = EvenStartZ
            for x in range(0, self._Size - 1, 2):
                TempTile = Tile(x, y, z, self._Size)
                self._Tiles.append(TempTile)
                y -= 1
                z -= 1
            EvenStartZ += 1
            EvenStartY -= 1
            y = OddStartY
            z = OddStartZ
            for x in range(1, self._Size, 2):
                TempTile = Tile(x, y, z, self._Size)
                self._Tiles.append(TempTile)
                y -= 1
                z -= 1
            OddStartZ += 1
            OddStartY -= 1

    def __SetUpNeighbours(self):
        for FromTile in self._Tiles:
            for ToTile in self._Tiles:
                if FromTile.GetDistanceToTileT(ToTile) == 1:
                    FromTile.AddToNeighbours(ToTile)

    def DestroyPiecesAndCountVPs(self):
        BaronDestroyed = False
        Player1VPs = 0
        Player2VPs = 0
        ListOfTilesContainingDestroyedPieces = []
        for T in self._Tiles:
            if T.GetPieceInTile() is not None:
                ListOfNeighbours = T.GetNeighbours()
                NoOfConnections = 0
                for N in ListOfNeighbours:
                    if N.GetPieceInTile() is not None:
                        NoOfConnections += 1
                ThePiece = T.GetPieceInTile()
                if NoOfConnections >= ThePiece.GetConnectionsNeededToDestroy():
                    ThePiece.DestroyPiece()
                    if ThePiece.GetPieceType().upper() == "B":
                        BaronDestroyed = True
                    ListOfTilesContainingDestroyedPieces.append(T)
                    if ThePiece.GetBelongsToPlayer1():
                        Player2VPs += ThePiece.GetVPs()
                    else:
                        Player1VPs += ThePiece.GetVPs()
        for T in ListOfTilesContainingDestroyedPieces:
            T.SetPiece(None)
        return BaronDestroyed, Player1VPs, Player2VPs

    def GetGridAsString(self, P1Turn):
        self.__ListPositionOfTile = 0
        self._Player1Turn = P1Turn
        GridAsString = self.__CreateTopLine() + self.__CreateEvenLine(True)
        self.__ListPositionOfTile += 1
        GridAsString += self.__CreateOddLine()
        for count in range(1, self._Size - 1, 2):
            self.__ListPositionOfTile += 1
            GridAsString += self.__CreateEvenLine(False)
            self.__ListPositionOfTile += 1
            GridAsString += self.__CreateOddLine()
        return GridAsString + self.__CreateBottomLine()

    def __MovePiece(self, NewIndex, OldIndex):
        self._Tiles[NewIndex].SetPiece(self._Tiles[OldIndex].GetPieceInTile())
        self._Tiles[OldIndex].SetPiece(None)

    def GetPieceTypeInTile(self, ID):
        ThePiece = self._Tiles[ID].GetPieceInTile()
        if ThePiece is None:
            return " "
        else:
            return ThePiece.GetPieceType()

    def __CreateBottomLine(self):
        Line = "   "
        for count in range(1, self._Size // 2 + 1):
            Line += " \\__/ "
        return Line + os.linesep

    def __CreateTopLine(self):
        Line = os.linesep + "  "
        for count in range(1, self._Size // 2 + 1):
            Line += "__    "
        return Line + os.linesep

    def __CreateOddLine(self):
        Line = ""
        for count in range(1, self._Size // 2 + 1):
            if count > 1 and count < self._Size // 2:
                Line += self.GetPieceTypeInTile(self.__ListPositionOfTile) + "\\__/"
                self.__ListPositionOfTile += 1
                Line += self._Tiles[self.__ListPositionOfTile].GetTerrain()
            elif count == 1:
                Line += " \\__/" + self._Tiles[self.__ListPositionOfTile].GetTerrain()
        Line += self.GetPieceTypeInTile(self.__ListPositionOfTile) + "\\__/"
        self.__ListPositionOfTile += 1
        if self.__ListPositionOfTile < len(self._Tiles):
            Line += (
                self._Tiles[self.__ListPositionOfTile].GetTerrain()
                + self.GetPieceTypeInTile(self.__ListPositionOfTile)
                + "\\"
                + os.linesep
            )
        else:
            Line += "\\" + os.linesep
        return Line

    def __CreateEvenLine(self, FirstEvenLine):
        Line = " /" + self._Tiles[self.__ListPositionOfTile].GetTerrain()
        for count in range(1, self._Size // 2):
            Line += self.GetPieceTypeInTile(self.__ListPositionOfTile)
            self.__ListPositionOfTile += 1
            Line += "\\__/" + self._Tiles[self.__ListPositionOfTile].GetTerrain()
        if FirstEvenLine:
            Line += (
                self.GetPieceTypeInTile(self.__ListPositionOfTile) + "\\__" + os.linesep
            )
        else:
            Line += (
                self.GetPieceTypeInTile(self.__ListPositionOfTile)
                + "\\__/"
                + os.linesep
            )
        return Line


class Player:
    def __init__(self, N, V, F, L, T):
        self._Name = N
        self._VPs = V
        self._Fuel = F
        self._Lumber = L
        self._PiecesInSupply = T

    def GetStateString(self):
        return (
            "VPs: "
            + str(self._VPs)
            + "   Pieces in supply: "
            + str(self._PiecesInSupply)
            + "   Lumber: "
            + str(self._Lumber)
            + "   Fuel: "
            + str(self._Fuel)
        )

    def GetVPs(self):
        return self._VPs

    def GetFuel(self):
        return self._Fuel

    def GetLumber(self):
        return self._Lumber

    def GetName(self):
        return self._Name

    def AddToVPs(self, n):
        self._VPs += n

    def UpdateFuel(self, n):
        self._Fuel += n

    def UpdateLumber(self, n):
        self._Lumber += n

    def GetPiecesInSupply(self):
        return self._PiecesInSupply

    def RemoveTileFromSupply(self):
        self._PiecesInSupply -= 1

    def GetCommands(self, TileList, isFirst=True):
        Commands = []
        print(
            self.GetName()
            + " state your three commands, pressing enter after each one."
        )
        for _ in range(1, 4):
            Commands.append(input("Enter command: ").lower())
        return Commands


#### NM AI STARTS HERE

PlayerAttributes = NewType("PlayerAttributes", Tuple[int, int, int, int])
# VPs, Fuel, Lumber, Pieces in supply
FlatTile = NewType("FlatTile", Tuple[str, str])
# Piece, Terrain
FlatBoard = NewType(
    "FlatBoard", Tuple[Tuple[FlatTile], PlayerAttributes, PlayerAttributes]
)


class Node:
    def __init__(
        self, command: str, resulting_board: FlatBoard, parent: Optional["Node"] = None
    ):
        self.command = command
        self.board = resulting_board
        self.hash = hash(resulting_board)
        self.children: List[Node] = []
        self.visits = 2
        self.p1_wins = 1
        self.parent = parent

    def __repr__(self):
        return f"<{self.command}, V{self.visits}, W{self.p1_wins}>"

    @staticmethod
    def _potential_moves(grid, grid_size, is_first):
        potential_moves = [[] for _ in grid]
        for index, (piece, _) in enumerate(grid):
            # piece, terrain are strs
            # if piece is the same as the current move then
            if piece.isupper() == is_first:
                # Checks whether an odd line
                potential_moves[index] = get_surrounding_positions(
                    index, grid_size, len(grid)
                )
        return potential_moves

    def update(self, p1_win: bool):
        self.visits += 1
        self.p1_wins += p1_win

    def _get_moves(self, is_first, fuel):
        grid = self.board[0]
        grid_size = int((len(grid) // 2) ** 0.5)
        potential_moves = self._potential_moves(grid, grid_size, is_first)
        move_eventualities = []
        for moving_piece_index, moving_to_indexes in enumerate(potential_moves):
            if (
                grid[moving_piece_index][1] == "#"
                and grid[moving_piece_index][0].upper() == "L"
            ):
                continue
            if (
                grid[moving_piece_index][1] == "~"
                and grid[moving_piece_index][0].upper() == "P"
            ):
                continue
            if not moving_to_indexes:
                continue
            for move in moving_to_indexes:
                if grid[move][0]:
                    continue
                if grid[moving_piece_index][0].upper() == "L":
                    if fuel < 1 or grid[moving_piece_index][1] == "#":
                        continue
                    elif (
                        "~" in (grid[moving_piece_index][1], grid[move][1])
                        and fuel >= 2
                    ):
                        new_board = get_board_after_move(
                            self.board, moving_piece_index, move, 2, is_first
                        )
                        move_eventualities.append(
                            Node(f"move {moving_piece_index} {move}", new_board, self)
                        )
                    else:
                        new_board = get_board_after_move(
                            self.board, moving_piece_index, move, 1, is_first
                        )
                        move_eventualities.append(
                            Node(f"move {moving_piece_index} {move}", new_board, self)
                        )
                elif grid[moving_piece_index][0].upper() == "P":
                    if fuel < 1 or grid[moving_piece_index][1] == "~":
                        continue
                    else:
                        new_board = get_board_after_move(
                            self.board, moving_piece_index, move, 2, is_first
                        )
                        move_eventualities.append(
                            Node(f"move {moving_piece_index} {move}", new_board, self)
                        )
                elif grid[moving_piece_index][0].upper() == "S":
                    if grid[move][1] == "~" and fuel > 2:
                        new_board = get_board_after_move(
                            self.board, moving_piece_index, move, 2, is_first
                        )
                        move_eventualities.append(
                            Node(f"move {moving_piece_index} {move}", new_board, self)
                        )
                    elif fuel < 1:
                        continue
                    else:
                        new_board = get_board_after_move(
                            self.board, moving_piece_index, move, 1, is_first
                        )
                        move_eventualities.append(
                            Node(f"move {moving_piece_index} {move}", new_board, self)
                        )
                elif grid[moving_piece_index][0].upper() == "B":
                    if fuel > 1:
                        new_board = get_board_after_move(
                            self.board, moving_piece_index, move, 1, is_first
                        )
                        move_eventualities.append(
                            Node(f"move {moving_piece_index} {move}", new_board, self)
                        )
        return move_eventualities

    def _get_digs_and_saws(self, is_first: bool) -> List["Node"]:
        move_eventualities = []
        for index, (piece, terrain) in enumerate(self.board[0]):
            if piece.isupper() != is_first:
                continue
            if piece.upper() == "P" and terrain == "~":
                command = f"dig {index}"
                if is_first:
                    new_board = get_modified_board(
                        self.board,
                        {},
                        PlayerAttributes(
                            (
                                self.board[1][0],
                                self.board[1][1] + 1,
                                self.board[1][2],
                                self.board[1][3],
                            )
                        ),
                    )
                else:
                    new_board = get_modified_board(
                        self.board,
                        {},
                        PlayerAttributes(
                            (
                                self.board[2][0],
                                self.board[2][1] + 1,
                                self.board[2][2],
                                self.board[2][3],
                            )
                        ),
                    )
                move_eventualities.append(Node(command, new_board, self))
            elif piece.upper() == "L" and terrain == "#":
                command = f"saw {index}"
                if is_first:
                    new_board = get_modified_board(
                        self.board,
                        {},
                        PlayerAttributes(
                            (
                                self.board[1][0],
                                self.board[1][1],
                                self.board[1][2] + 1,
                                self.board[1][3],
                            )
                        ),
                    )
                else:
                    new_board = get_modified_board(
                        self.board,
                        {},
                        PlayerAttributes(
                            (
                                self.board[2][0],
                                self.board[2][1],
                                self.board[2][2] + 1,
                                self.board[2][3],
                            )
                        ),
                    )
                move_eventualities.append(Node(command, new_board, self))
        return move_eventualities

    def _get_spawns(self, is_first: bool):
        if (
            self.board[1 if is_first else 2][3] < 1
            or self.board[1 if is_first else 2][2] < 3
        ):
            return []
        grid = self.board[0]
        spawns = []
        grid_size = int((len(grid) // 2) ** 0.5)
        for index, (piece, _) in enumerate(self.board[0]):
            if piece.isupper() == is_first and piece.upper() == "B":
                sp = get_surrounding_positions(index, grid_size, len(grid))
                for position_index in sp:
                    if self.board[0][position_index][0]:
                        continue
                    command = f"spawn {position_index}"
                    new_board = get_modified_board(
                        self.board,
                        {
                            position_index: FlatTile(
                                (
                                    "S" if is_first else "s",
                                    self.board[0][position_index][1],
                                )
                            )
                        },
                        new_p1_attributes=(
                            PlayerAttributes(
                                (
                                    self.board[1][0],
                                    self.board[1][1],
                                    self.board[1][2] - 3,
                                    self.board[1][3] - 1,
                                )
                            )
                            if is_first
                            else None
                        ),
                        new_p2_attributes=(
                            PlayerAttributes(
                                (
                                    self.board[2][0],
                                    self.board[2][1],
                                    self.board[2][2] - 3,
                                    self.board[2][3] - 1,
                                )
                            )
                            if not is_first
                            else None
                        ),
                    )
                    spawns.append(Node(command, new_board, self))
        return spawns

    def _get_upgrades(self, is_first: bool):
        if self.board[1 if is_first else 2][2] < 5:
            return []
        upgrades = []
        for index, (piece, _) in enumerate(self.board[0]):
            if piece.isupper() == is_first and piece.upper() == "S":
                for upgrade_piece in ("pbds", "less"):
                    command = f"upgrade {upgrade_piece} {index}"
                    new_piece = (
                        upgrade_piece[0].upper() if is_first else upgrade_piece[0]
                    )
                    new_board = get_modified_board(
                        self.board,
                        {index: FlatTile((new_piece, self.board[0][index][1]))},
                        new_p1_attributes=(
                            PlayerAttributes(
                                (
                                    self.board[1][0],
                                    self.board[1][1],
                                    self.board[1][2] - 5,
                                    self.board[1][3],
                                )
                            )
                            if is_first
                            else None
                        ),
                        new_p2_attributes=(
                            PlayerAttributes(
                                (
                                    self.board[2][0],
                                    self.board[2][1],
                                    self.board[2][2] - 5,
                                    self.board[2][3],
                                )
                            )
                            if not is_first
                            else None
                        ),
                    )
                    upgrades.append(Node(command, new_board, self))
        return upgrades

    def get_next_actions(self, is_first: bool) -> List["Node"]:
        all_next_actions = []
        all_next_actions.extend(
            self._get_moves(is_first, self.board[1 if is_first else 2][2])
        )
        all_next_actions.extend(self._get_digs_and_saws(is_first))
        all_next_actions.extend(self._get_spawns(is_first))
        all_next_actions.extend(self._get_upgrades(is_first))
        return all_next_actions

    def check_destroyed_pieces_vps(self):
        p1_vps = 0
        p2_vps = 0
        destroyed = []
        grid = self.board[0]
        grid_size = int((len(grid) // 2) ** 0.5)
        vp_map = {"B": 10, "S": 1, "L": 3, "P": 2}
        for index, (piece, _) in enumerate(grid):
            if not piece:
                continue
            surrounding = 0
            for pos in get_surrounding_positions(index, grid_size, len(grid)):
                if grid[pos][0]:
                    surrounding += 1
            if surrounding >= 2:
                if piece.isupper():
                    p2_vps += vp_map[piece.upper()]
                else:
                    p1_vps += vp_map[piece.upper()]
                destroyed.append(index)
        new_grid = get_modified_board(
            self.board,
            {index: FlatTile(("", grid[index][1])) for index in destroyed},
            new_p1_attributes=(
                PlayerAttributes(
                    (
                        self.board[1][0] + p1_vps,
                        self.board[1][1],
                        self.board[1][2],
                        self.board[1][3],
                    )
                )
            ),
            new_p2_attributes=(
                PlayerAttributes(
                    (
                        self.board[2][0] + p2_vps,
                        self.board[2][1],
                        self.board[2][2],
                        self.board[2][3],
                    )
                )
            ),
        )
        command = ""
        return Node(command, new_grid, self)

    def check_win(self) -> Tuple[bool, bool]:  # (is_win, p1_win)
        is_p1_baron = False
        is_p2_baron = False
        for piece, _ in self.board[0]:
            if piece == "B":
                is_p1_baron = True
            elif piece == "b":
                is_p2_baron = True
        if is_p1_baron and is_p2_baron:
            return (False, False)
        return (True, self.board[1][0] > self.board[2][0])

    def get_best_child(self, p1: bool) -> "Node":
        current_best = Fraction(0)
        max_nodes = []
        for child in self.children:
            cf = Fraction(
                child.p1_wins if p1 else (child.visits - child.p1_wins), child.visits
            )
            if cf > current_best:
                max_nodes = [child]
                current_best = cf
            elif cf == current_best:
                max_nodes.append(child)
        return choice(max_nodes)


def get_surrounding_positions(index, grid_size, grid_length):
    surrounding_positions = []
    if index % (2 * grid_size) < grid_size:
        # Saves a couple of operations in some cases by writing if-statements like this
        if index > (2 * grid_size):
            surrounding_positions.append(index - (2 * grid_size))
            surrounding_positions.append(index - (grid_size + 1))
            surrounding_positions.append(index - grid_size)
        elif index > (grid_size + 1) and index % (2 * grid_size) != 0:
            surrounding_positions.append(index - (grid_size + 1))
            surrounding_positions.append(index - grid_size)
        elif index > grid_size:
            surrounding_positions.append(index - grid_size)
        if index + (2 * grid_size) < grid_length:
            surrounding_positions.append(index + (2 * grid_size))
            surrounding_positions.append(index + grid_size)
            if index % (2 * grid_size) != 0:
                surrounding_positions.append(index + (grid_size - 1))
        elif index + grid_size < grid_length:
            surrounding_positions.append(index + grid_size)
            if index % (2 * grid_size) != 0:
                surrounding_positions.append(index + (grid_size - 1))
        elif index + (grid_size - 1) < grid_length and index % (2 * grid_size) != 0:
            surrounding_positions.append(index + (grid_size - 1))
    else:
        if index > (2 * grid_size):
            surrounding_positions.append(index - (2 * grid_size))
            if index % (2 * grid_size) != (2 * grid_size) - 1:
                surrounding_positions.append(index - (grid_size + 1))
            surrounding_positions.append(index - grid_size)
        elif index > (grid_size + 1) and index % (2 * grid_size) != (2 * grid_size) - 1:
            surrounding_positions.append(index - (grid_size + 1))
            surrounding_positions.append(index - grid_size)
        elif index > grid_size:
            surrounding_positions.append(index - grid_size)
        if index + (2 * grid_size) < grid_length:
            surrounding_positions.append(index + (2 * grid_size))
            surrounding_positions.append(index + grid_size)
            surrounding_positions.append(index + (grid_size + 1))
        elif index + grid_size < grid_length:
            surrounding_positions.append(index + grid_size)
            surrounding_positions.append(index + (grid_size + 1))
        elif (
            index + (grid_size + 1) < grid_length
            and index % (2 * grid_size) != (2 * grid_size) - 1
        ):
            surrounding_positions.append(index + (grid_size + 1))
    return surrounding_positions


def get_modified_board(
    start: FlatBoard,
    mapping: Dict[int, FlatTile],
    new_p1_attributes: Optional[PlayerAttributes] = None,
    new_p2_attributes: Optional[PlayerAttributes] = None,
) -> FlatBoard:
    board = start[0]
    p1_attributes = start[1]
    p2_attributes = start[2]
    for index, tile in mapping.items():
        board = board[:index] + (tile,) + board[index + 1 :]
    if new_p1_attributes is not None:
        p1_attributes = new_p1_attributes
    if new_p2_attributes is not None:
        p2_attributes = new_p2_attributes
    return (board, p1_attributes, p2_attributes)


def get_board_after_move(
    board: FlatBoard, move_from: int, move_to: int, fuel_cost: int, p1_turn: bool
) -> FlatBoard:
    return get_modified_board(
        board,
        {
            move_from: FlatTile(("", board[0][move_from][1])),
            move_to: FlatTile((board[0][move_from][0], board[0][move_to][1])),
        },
        PlayerAttributes(
            (board[1][0], board[1][1] - fuel_cost, board[1][2], board[1][3])
        )
        if p1_turn
        else None,
        PlayerAttributes(
            (board[2][0], board[2][1] - fuel_cost, board[2][2], board[2][3])
        )
        if not p1_turn
        else None,
    )


class MCTSBot(Player):
    def __init__(self, N, V, F, L, T, opponent: Player):
        super().__init__(N, V, F, L, T)
        self.tree_nodes = {}
        self.timer_on = False
        self.opponent = opponent

    def GetCommands(self, tilelist: List[Tile], isFirst: bool = True) -> List[str]:
        opponent = self.opponent
        current_board = self.get_flat_board(tilelist, opponent, isFirst)
        if hash(current_board) in self.tree_nodes:
            current_node = self.tree_nodes[hash(current_board)]
        else:
            current_node = Node("", current_board)
            self.tree_nodes[current_node.hash] = current_node
        return self.mcts(current_node, isFirst)

    def turn_off_timer(self):
        self.timer_on = False

    def mcts(self, current_node: Node, p1: bool):
        self.timer_on = True
        t = Timer(2, self.turn_off_timer)
        t.start()
        top_node: Node = current_node
        while self.timer_on:
            is_p1_turn: bool = p1
            turn_counter = 0
            current_node = top_node
            s = []
            while current_node.children:
                if not current_node.children:
                    break
                current_node = current_node.get_best_child(is_p1_turn)
                turn_counter += 1
                if turn_counter == 4:
                    turn_counter = 0
                    is_p1_turn = not is_p1_turn
                s.append(current_node.command)
            new_node = current_node
            loop_count = 0
            while True:
                loop_count += 1
                if loop_count > 2000:
                    break
                if turn_counter == 3:
                    new_node.children = [new_node.check_destroyed_pieces_vps()]
                    new_node = new_node.children[0]
                    turn_counter = 0
                    is_p1_turn = not is_p1_turn
                    is_win, p1_win = new_node.check_win()
                    if is_win:
                        while current_node.parent:
                            current_node.update(p1_win)
                            current_node = current_node.parent
                        break
                else:
                    new_node.children.extend(new_node.get_next_actions(is_p1_turn))
                    turn_counter += 1
                    if new_node.children == []:
                        break
                    new_node = choice(new_node.children)
        final_states = []
        end_node = top_node
        for _ in range(3):
            end_node = end_node.get_best_child(p1)
            final_states.append(end_node.command)
        # print(top_node.children)
        return final_states

    def get_flat_board(self, tilelist: List[Tile], opponent: Player, isFirst: bool):
        if isFirst:
            p1_attributes = PlayerAttributes(
                (self._VPs, self._Fuel, self._Lumber, self._PiecesInSupply)
            )
            p2_attributes = PlayerAttributes(
                (
                    opponent.GetVPs(),
                    opponent.GetFuel(),
                    opponent.GetLumber(),
                    opponent.GetPiecesInSupply(),
                )
            )
        else:
            p2_attributes = PlayerAttributes(
                (self._VPs, self._Fuel, self._Lumber, self._PiecesInSupply)
            )
            p1_attributes = PlayerAttributes(
                (
                    opponent.GetVPs(),
                    opponent.GetFuel(),
                    opponent.GetLumber(),
                    opponent.GetPiecesInSupply(),
                )
            )
        board = tuple(
            FlatTile(
                (
                    (
                        tile.GetPieceInTile().GetPieceType()
                        if tile.GetPieceInTile()
                        else ""
                    ),
                    tile.GetTerrain(),
                )
            )
            for tile in tilelist
        )
        return FlatBoard((board, p1_attributes, p2_attributes))


#### NM AI ENDS HERE


class SecondAI(Player):
    def GetCommands(self, TileList, isFirst=True):
        MyBaron = "B" if isFirst else "b"
        BaronTile = TileList[0]
        for Space in TileList:
            if (
                Space.GetPieceInTile()
                and Space.GetPieceInTile().GetPieceType() == MyBaron
            ):
                BaronTile = Space
        FreeNeighbors = []
        for NeighboringTile in BaronTile.GetNeighbours():
            if not NeighboringTile.GetPieceInTile():
                FreeNeighbors.append(NeighboringTile)
        MoveOrigin = BaronTile.GetId()
        MoveDestination = random.choice(FreeNeighbors)
        IsBaronSafe = True
        SpawnLocales = []
        for NeighboringTile in MoveDestination.GetNeighbours():
            if (
                NeighboringTile.GetPieceInTile()
                and not NeighboringTile.GetId() == MoveOrigin
            ):
                IsBaronSafe = False
            elif not NeighboringTile.GetId() == MoveOrigin:
                SpawnLocales.append(NeighboringTile.GetId())
        if IsBaronSafe:
            SecondCommand = "spawn {0}".format(random.choice(SpawnLocales))
        else:
            SecondCommand = "dig {0}".format(MoveDestination.GetId())
        return [
            "move {0} {1}".format(MoveOrigin, MoveDestination.GetId()),
            SecondCommand,
            "saw {0}".format(MoveDestination.GetId()),
        ]


# OTHER AI GOES HERE


# class SecondAI(player_two_bot):
#     pass

# OTHER AI GOES HERE


def Main():
    FileLoaded = True
    Player1 = None
    Player2 = None
    Grid = None
    Choice = ""
    while Choice != "Q":
        DisplayMainMenu()
        Choice = input()
        if Choice == "1":
            Player1, Player2, Grid = SetUpDefaultGame()
            PlayGame(Player1, Player2, Grid)
        elif Choice == "2":
            FileLoaded, Player1, Player2, Grid = LoadGame()
            if FileLoaded:
                PlayGame(Player1, Player2, Grid)
        elif Choice == "3":
            Player1, Player2, Grid = SetUpDefaultGameAgainstAI()
            PlayGame(Player1, Player2, Grid)
        elif Choice == "4":
            Player1, Player2, Grid = SetUpRandomGame(AICount=0)
            PlayGame(Player1, Player2, Grid)
        elif Choice == "5":
            Player1, Player2, Grid = SetUpRandomGame(AICount=1)
            PlayGame(Player1, Player2, Grid)
        elif Choice == "6":
            Player1, Player2, Grid = SetUpRandomGame(AICount=2)
            PlayGame(Player1, Player2, Grid)


def LoadGame():
    FileName = input("Enter the name of the file to load: ")
    Items = []
    LineFromFile = ""
    Player1 = None
    Player2 = None
    Grid = None
    try:
        with open(FileName) as f:
            LineFromFile = f.readline().rstrip()
            Items = LineFromFile.split(",")
            Player1 = Player(
                Items[0], int(Items[1]), int(Items[2]), int(Items[3]), int(Items[4])
            )
            LineFromFile = f.readline().rstrip()
            Items = LineFromFile.split(",")
            Player2 = Player(
                Items[0], int(Items[1]), int(Items[2]), int(Items[3]), int(Items[4])
            )
            GridSize = int(f.readline().rstrip())
            Grid = HexGrid(GridSize)
            T = f.readline().rstrip().split(",")
            Grid.SetUpGridTerrain(T)
            LineFromFile = f.readline().rstrip()
            while LineFromFile != "":
                Items = LineFromFile.split(",")
                if Items[0] == "1":
                    Grid.AddPiece(True, Items[1], int(Items[2]))
                else:
                    Grid.AddPiece(False, Items[1], int(Items[2]))
                LineFromFile = f.readline().rstrip()
    except:
        print("File not loaded")
        return False, Player1, Player2, Grid
    return True, Player1, Player2, Grid


def SetUpDefaultGame():
    T = [
        " ",
        "#",
        "#",
        " ",
        "~",
        "~",
        " ",
        " ",
        " ",
        "~",
        " ",
        "#",
        "#",
        " ",
        " ",
        " ",
        " ",
        " ",
        "#",
        "#",
        "#",
        "#",
        "~",
        "~",
        "~",
        "~",
        "~",
        " ",
        "#",
        " ",
        "#",
        " ",
    ]
    GridSize = 8
    Grid = HexGrid(GridSize)
    Player1 = Player("Player One", 0, 10, 10, 5)
    Player2 = Player("Player Two", 1, 10, 10, 5)
    Grid.SetUpGridTerrain(T)
    Grid.AddPiece(True, "Baron", 0)
    Grid.AddPiece(True, "Serf", 8)
    Grid.AddPiece(False, "Baron", 31)
    Grid.AddPiece(False, "Serf", 23)
    return Player1, Player2, Grid


def SetUpRandomGame(
    ForestProbability=0.3,
    PeatBogProbability=0.3,
    MinGridSize=8,
    MaxGridSize=12,
    AICount=0,
):
    # Supply Cap is GridSize - 3
    # Available Lumber and Fuel is between GridSize and double GridSize
    T = [" "]
    # GridSize = (
    #     random.randint((MinGridSize + 1) // 2, MaxGridSize // 2) * 2
    # )  # has to be even
    GridSize = 8
    for _ in range(GridSize * GridSize // 2 - 2):
        TerrainSeed = random.random()
        if TerrainSeed < PeatBogProbability:
            T.append("~")
        elif TerrainSeed < PeatBogProbability + ForestProbability:
            T.append("#")
        else:
            T.append(" ")
    T.append(" ")
    Grid = HexGrid(GridSize)
    StartingLumber = GridSize + random.randint(1, GridSize)
    StartingFuel = GridSize + random.randint(1, GridSize)
    SupplyCap = GridSize - 3
    if AICount == 0:
        Player1 = Player("Player One", 0, StartingLumber, StartingFuel, SupplyCap)
        Player2 = Player("Player Two", 1, StartingLumber, StartingFuel, SupplyCap)
    elif AICount == 1:
        AiStarts = random.choice([True, False])
        if AiStarts:
            print("AI Player goes first.")
            Player2 = Player("Human Player", 1, StartingLumber, StartingFuel, SupplyCap)
            Player1 = MCTSBot(
                "AI Player", 0, StartingLumber, StartingFuel, SupplyCap, Player2
            )
        else:
            print("Human Player goes first")
            Player1 = Player("Human Player", 0, StartingLumber, StartingFuel, SupplyCap)
            Player2 = MCTSBot(
                "AI Player", 1, StartingLumber, StartingFuel, SupplyCap, Player1
            )
    elif AICount == 2:
        Player2 = SecondAI("AI Player Two", 1, StartingLumber, StartingFuel, SupplyCap)
        Player1 = MCTSBot(
            "AI Player One", 0, StartingLumber, StartingFuel, SupplyCap, Player2
        )
    Grid.SetUpGridTerrain(T)
    Grid.AddPiece(True, "Baron", 0)
    Grid.AddPiece(True, "Serf", GridSize)
    Grid.AddPiece(False, "Baron", GridSize * GridSize // 2 - 1)
    Grid.AddPiece(False, "Serf", GridSize * GridSize // 2 - GridSize - 1)
    return Player1, Player2, Grid


def SetUpDefaultGameAgainstAI():
    T = [
        " ",
        "#",
        "#",
        " ",
        "~",
        "~",
        " ",
        " ",
        " ",
        "~",
        " ",
        "#",
        "#",
        " ",
        " ",
        " ",
        " ",
        " ",
        "#",
        "#",
        "#",
        "#",
        "~",
        "~",
        "~",
        "~",
        "~",
        " ",
        "#",
        " ",
        "#",
        " ",
    ]
    AiStarts = random.choice([True, False])
    GridSize = 8
    Grid = HexGrid(GridSize)
    if AiStarts:
        print("AI Player goes first.")
        Player2 = Player("Human Player", 1, 10, 10, 5)
        Player1 = MCTSBot("AI Player", 0, 10, 10, 5, Player2)
    else:
        print("Human Player goes first")
        Player1 = Player("Human Player", 0, 10, 10, 5)
        Player2 = MCTSBot("AI Player", 1, 10, 10, 5, Player1)
    Grid.SetUpGridTerrain(T)
    Grid.AddPiece(True, "Baron", 0)
    Grid.AddPiece(True, "Serf", 8)
    Grid.AddPiece(False, "Baron", 31)
    Grid.AddPiece(False, "Serf", 23)
    return Player1, Player2, Grid


def CheckMoveCommandFormat(Items):
    if len(Items) == 3:
        for Count in range(1, 3):
            try:
                Result = int(Items[Count])
            except:
                return False
        return True
    return False


def CheckStandardCommandFormat(Items):
    if len(Items) == 2:
        try:
            Result = int(Items[1])
        except:
            return False
        return True
    return False


def CheckUpgradeCommandFormat(Items):
    if len(Items) == 3:
        if Items[1].upper() != "LESS" and Items[1].upper() != "PBDS":
            return False
        try:
            Result = int(Items[2])
        except:
            return False
        return True
    return False


def CheckCommandIsValid(Items):
    if len(Items) > 0:
        if Items[0] == "move":
            return CheckMoveCommandFormat(Items)
        elif Items[0] in ["dig", "saw", "spawn"]:
            return CheckStandardCommandFormat(Items)
        elif Items[0] == "upgrade":
            return CheckUpgradeCommandFormat(Items)
    return False


def PlayGame(Player1, Player2, Grid):
    GameOver = False
    Player1Turn = True
    Commands = []
    print("Player One current state - " + Player1.GetStateString())
    print("Player Two current state - " + Player2.GetStateString())
    while not (GameOver and Player1Turn):
        print(Grid.GetGridAsString(Player1Turn))
        if Player1Turn:
            Commands = Player1.GetCommands(Grid.GetTiles())
            print("Commands issued by Player 1:", Commands)
        else:
            Commands = Player2.GetCommands(Grid.GetTiles(), isFirst=False)
            print("Commands issued by Player 2:", Commands)

        for C in Commands:
            Items = C.split(" ")
            ValidCommand = CheckCommandIsValid(Items)
            if not ValidCommand:
                print("Invalid command")
            else:
                FuelChange = 0
                LumberChange = 0
                SupplyChange = 0
                if Player1Turn:
                    (
                        SummaryOfResult,
                        FuelChange,
                        LumberChange,
                        SupplyChange,
                    ) = Grid.ExecuteCommand(
                        Items,
                        Player1.GetFuel(),
                        Player1.GetLumber(),
                        Player1.GetPiecesInSupply(),
                    )
                    Player1.UpdateLumber(LumberChange)
                    Player1.UpdateFuel(FuelChange)
                    if SupplyChange == 1:
                        Player1.RemoveTileFromSupply()
                else:
                    (
                        SummaryOfResult,
                        FuelChange,
                        LumberChange,
                        SupplyChange,
                    ) = Grid.ExecuteCommand(
                        Items,
                        Player2.GetFuel(),
                        Player2.GetLumber(),
                        Player2.GetPiecesInSupply(),
                    )
                    Player2.UpdateLumber(LumberChange)
                    Player2.UpdateFuel(FuelChange)
                    if SupplyChange == 1:
                        Player2.RemoveTileFromSupply()
                print(SummaryOfResult)
        Commands.clear()
        Player1Turn = not Player1Turn
        Player1VPsGained = 0
        Player2VPsGained = 0
        if GameOver:
            (
                GameOver,
                Player1VPsGained,
                Player2VPsGained,
            ) = Grid.DestroyPiecesAndCountVPs()
            GameOver = True
        else:
            (
                GameOver,
                Player1VPsGained,
                Player2VPsGained,
            ) = Grid.DestroyPiecesAndCountVPs()
        Player1.AddToVPs(Player1VPsGained)
        Player2.AddToVPs(Player2VPsGained)
        print("Player One current state - " + Player1.GetStateString())
        print("Player Two current state - " + Player2.GetStateString())
        input("Press Enter to continue...")
    print(Grid.GetGridAsString(Player1Turn))
    DisplayEndMessages(Player1, Player2)


def DisplayEndMessages(Player1, Player2):
    print()
    print(Player1.GetName() + " final state: " + Player1.GetStateString())
    print()
    print(Player2.GetName() + " final state: " + Player2.GetStateString())
    print()
    if Player1.GetVPs() > Player2.GetVPs():
        print(Player1.GetName() + " is the winner!")
    else:
        print(Player2.GetName() + " is the winner!")


def DisplayMainMenu():
    print("1. Default game")
    print("2. Load game")
    print("3. Default game against AI")
    print("4. Randomized two-player game")
    print("5. Randomized game against AI")
    print("6. Randomized game between AIs")
    print("Q. Quit")
    print()
    print("Enter your choice: ", end="")


if __name__ == "__main__":
    Main()
