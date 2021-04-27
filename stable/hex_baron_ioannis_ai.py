# Skeleton Program code for the AQA A Level Paper 1 Summer 2021 examination
# this code should be used in conjunction with the Preliminary Material
# written by the AQA Programmer Team
# developed in the Python 3.5 programming environment

import random
import os


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
    '''ADDED GRIDSIZE ATTRIBUTE FOR REPR'''
    def __init__(self, xcoord, ycoord, zcoord, gridSize):
        self._x = xcoord
        self._y = ycoord
        self._z = zcoord
        self._Terrain = " "
        self._PieceInTile = None
        self._Neighbours = []
        self._id = (gridSize * (self._z - self._y) + self._x) // 2  
        self.gridsize = gridSize

    def GetDistanceToTileT(self, T):
        return max(max(abs(self.Getx() - T.Getx()), abs(self.Gety() - T.Gety())), abs(self.Getz() - T.Getz()))

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
        id = (self.gridsize * (self._z - self._y) + self._x) // 2
        neighbours = "Neighbours: " + ",".join(map(lambda x: str(x.GetId()), self._Neighbours))
        if self._PieceInTile:
            return ("Tile " + str(id) + ", position " + position + ". " + neighbours + ", occupied by " +
            self._PieceInTile.GetPieceType() + "\n")
        else:
            return ("Tile " + str(id) + ", position " + position + ". " + neighbours + ", free\n")


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
            Success, FuelChange, LumberChange = self.__ExecuteCommandInTile(
                Items)
            if not Success:
                return "Couldn't do that", FuelChange, LumberChange, SupplyChange
        elif Items[0] == "spawn":
            LumberCost = self.__ExecuteSpawnCommand(
                Items, LumberAvailable, PiecesInSupply)
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
        if not self.__CheckPieceAndTileAreValid(StartID) or not self.__CheckTileIndexIsValid(EndID):
            return -1
        ThePiece = self._Tiles[StartID].GetPieceInTile()
        if self._Tiles[EndID].GetPieceInTile() is not None:
            return -1
        Distance = self._Tiles[StartID].GetDistanceToTileT(self._Tiles[EndID])
        FuelCost = ThePiece.CheckMoveIsValid(
            Distance, self._Tiles[StartID].GetTerrain(), self._Tiles[EndID].GetTerrain())
        if FuelCost == -1 or FuelAvailable < FuelCost:
            return -1
        self.__MovePiece(EndID, StartID)
        return FuelCost

    def __ExecuteSpawnCommand(self, Items, LumberAvailable, PiecesInSupply):
        TileToUse = int(Items[1])
        if PiecesInSupply < 1 or LumberAvailable < 3 or not self.__CheckTileIndexIsValid(TileToUse):
            return -1
        ThePiece = self._Tiles[TileToUse].GetPieceInTile()
        if ThePiece is not None:
            return -1
        OwnBaronIsNeighbour = False
        ListOfNeighbours = self._Tiles[TileToUse].GetNeighbours()
        for N in ListOfNeighbours:
            ThePiece = N.GetPieceInTile()
            if ThePiece is not None:
                if self._Player1Turn and ThePiece.GetPieceType() == "B" or not self._Player1Turn and ThePiece.GetPieceType() == "b":
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
        if not self.__CheckPieceAndTileAreValid(TileToUse) or LumberAvailable < 5 or not (Items[1] == "pbds" or Items[1] == "less"):
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
                Line += self.GetPieceTypeInTile(
                    self.__ListPositionOfTile) + "\\__/"
                self.__ListPositionOfTile += 1
                Line += self._Tiles[self.__ListPositionOfTile].GetTerrain()
            elif count == 1:
                Line += " \\__/" + \
                    self._Tiles[self.__ListPositionOfTile].GetTerrain()
        Line += self.GetPieceTypeInTile(self.__ListPositionOfTile) + "\\__/"
        self.__ListPositionOfTile += 1
        if self.__ListPositionOfTile < len(self._Tiles):
            Line += self._Tiles[self.__ListPositionOfTile].GetTerrain(
            ) + self.GetPieceTypeInTile(self.__ListPositionOfTile) + "\\" + os.linesep
        else:
            Line += "\\" + os.linesep
        return Line

    def __CreateEvenLine(self, FirstEvenLine):
        Line = " /" + self._Tiles[self.__ListPositionOfTile].GetTerrain()
        for count in range(1, self._Size // 2):
            Line += self.GetPieceTypeInTile(self.__ListPositionOfTile)
            self.__ListPositionOfTile += 1
            Line += "\\__/" + \
                self._Tiles[self.__ListPositionOfTile].GetTerrain()
        if FirstEvenLine:
            Line += self.GetPieceTypeInTile(
                self.__ListPositionOfTile) + "\\__" + os.linesep
        else:
            Line += self.GetPieceTypeInTile(self.__ListPositionOfTile) + \
                "\\__/" + os.linesep
        return Line


class Player:
    def __init__(self, N, V, F, L, T):
        self._Name = N
        self._VPs = V
        self._Fuel = F
        self._Lumber = L
        self._PiecesInSupply = T

    def GetStateString(self):
        return "VPs: " + str(self._VPs) + "   Pieces in supply: " + str(self._PiecesInSupply) + "   Lumber: " + str(self._Lumber) + "   Fuel: " + str(self._Fuel)

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
        print(self.GetName() + " state your three commands, pressing enter after each one.")
        for _ in range(1, 4):
            Commands.append(input("Enter command: ").lower())
        return Commands


class FirstAI(Player):
    def __init__(self, N, V, F, L, T):
        super(FirstAI, self).__init__(N, V, F, L, T)
        self.DefenceTileCoordinates = []
        self.DefenceTiles = []

    def CreateDefenceTilesAndDefenceTileCoordinates(self, TileList, isFirst):
        if isFirst:
            DefenceTileCoordinates = [(2,-1,-1),(1,-2,1)]
        else:
            GridSize = self.GetGridSize(TileList)
            DefenceTileCoordinates = [(2*GridSize-3,-(2*GridSize-2),1),(2*GridSize-2,-(2*GridSize-3),-1)]
        self.DefenceTileCoordinates = DefenceTileCoordinates
        self.DefenceTiles = self.ReturnTileObjectsFromDefenceTileCoordinates(DefenceTileCoordinates, TileList)
    
    def GetTilesNeighbouringTwoTiles(self, Tile1, Tile2):
        NeighbouringTiles = []
        for Tile1NeighboringTile in Tile1.GetNeighbours():
            for Tile2NeighboringTile in Tile2.GetNeighbours():
                if Tile1NeighboringTile == Tile2NeighboringTile:
                    NeighbouringTiles.append(Tile1NeighboringTile)
        return NeighbouringTiles

    def CreateMoveCommand(self, StartIndex, DestinationIndex):
        return 'move ' + str(StartIndex) + ' ' + str(DestinationIndex)

    def CreateSpawnCommand(self, SpawnIndex):
        return 'spawn ' + str(SpawnIndex)

    def CreateUpgradeCommand(self, NewPiece, UpgradeIndex):
        return 'upgrade ' + NewPiece + ' ' + str(UpgradeIndex)

    def CreateSawCommand(self, SawIndex):
        return 'saw ' + str(SawIndex)

    def CreateDigCommand(self, DigIndex):
        return 'dig ' + str(DigIndex)

    def GetEnemyTiles(self, TileList, isFirst):
        return [Tile for Tile in TileList if Tile.GetPieceInTile() and Tile.GetPieceInTile().isupper() == isFirst]

    def TilesAreNeighbours(self, Tile1, Tile2):
        return Tile1 in Tile2.GetNeighbours()

    def GetTilesThatDestroyTwoEnemyPieces(self, TileList, isFirst):
        EnemyTileList = self.GetEnemyTiles(TileList, isFirst)
        Tiles = []
        for i in range(len(EnemyTileList)):
            EnemyTile1 = EnemyTileList[i]
            for j in range(i+1,len(EnemyTileList)):
                EnemyTile2 = EnemyTileList[j]
                if self.TilesAreNeighbours(EnemyTile1, EnemyTile2):
                    Tiles += self.GetTilesNeighbouringTwoTiles(EnemyTile1, EnemyTile2)
        return Tiles

    def GetGridSize(self, TileList):
        return (int(0.5*len(TileList)))**0.5

    def GetDistancedTiles(self, TileList, isFirst):
        DistancedTiles = []
        for Tile in TileList:
            Neighbours = Tile.GetNeighbours()
            NeighbouringPieces = [Neighbour for Neighbour in Neighbours if Neighbour.GetPieceInTile() != None]
            if len(NeighbouringPieces) == 0 and not Tile.GetPieceInTile():
                DistancedTiles.append(Tile)
        return DistancedTiles

    def GetNonProtectingSerfTiles(self, TileList, isFirst):
        Tiles = []
        for Tile in TileList:
            if Tile not in self.DefenceTiles and Tile.GetPieceInTile():
                if Tile.GetPieceInTile().GetPieceType().upper() == 'S' and Tile.GetPieceInTile().GetPieceType().isupper() == isFirst:
                    Tiles.append(Tile)
        return Tiles

    def GetMoreFuel(self, TileList, isFirst, NumberOfMovesLeft):
        Commands = []
        PBDSPieces = self.GetPBDSPieces(TileList, isFirst)
        PBDSPieces = [Tile for Tile in PBDSPieces if Tile.GetTerrain() == '~']
        if not PBDSPieces:
            return Commands
        PBDSPieceIndex = PBDSPieces[0].GetId()
        for i in range(NumberOfMovesLeft):
            Commands.append(self.CreateDigCommand(PBDSPieceIndex))
        return Commands

    def GetMoreLumber(self, TileList, isFirst, NumberOfMovesLeft):
        Commands = []
        LESSPieces = self.GetLESSPieces(TileList, isFirst)
        LESSPieces = [Tile for Tile in LESSPieces if Tile.GetTerrain() == '#']
        if not LESSPieces:
            return Commands
        LESSPieceIndex = LESSPieces[0].GetId()
        for i in range(NumberOfMovesLeft):
            Commands.append(self.CreateSawCommand(LESSPieceIndex))
        return Commands

    def GetBaronPieces(self, TileList, isFirst):
        return self.GetGivenPlayerPieceType(TileList, isFirst, 'B')

    def GetSerfPieces(self, TileList, isFirst):
        return self.GetGivenPlayerPieceType(TileList, isFirst, 'S')

    def GetPBDSPieces(self, TileList, isFirst):
        return self.GetGivenPlayerPieceType(TileList, isFirst, 'P')
        
    def GetLESSPieces(self, TileList, isFirst):
        return self.GetGivenPlayerPieceType(TileList, isFirst, 'L')

    def GetGivenPlayerPieceType(self, TileList, isFirst, Piece):
        return [Tile for Tile in self.GetPieceTiles(TileList, isFirst) if Tile.GetPieceInTile().GetPieceType().upper() == Piece and Tile.GetPieceInTile().GetPieceType().isupper() == isFirst]
        
    def GetPieceTiles(self, TileList, isFirst):
        return list(set(TileList)-set([Tile for Tile in TileList if not Tile.GetPieceInTile()]))

    def CreateProtectingSerfFormation(self, TileList, isFirst):
        if isFirst:
            DefenceTileCoordinates = [(2,-1,-1),(1,-2,1)]
        else:
            GridSize = self.GetGridSize(TileList)
            DefenceTileCoordinates = [(2*GridSize-3,-(2*GridSize-2),1),(2*GridSize-2,-(2*GridSize-3),-1)]
        self.DefenceTileCoordinates = DefenceTileCoordinates
        DefenceTileCoordinatesFilled = [False]*len(DefenceTileCoordinates)
        DefenceTiles = self.ReturnTileObjectsFromDefenceTileCoordinates(DefenceTileCoordinates, TileList)
        self.DefenceTiles = DefenceTiles
        Commands = []
        for DefenceTile in DefenceTiles:
            Neighbours = DefenceTile.GetNeighbours()
            for Neighbour in Neighbours:
                if not Neighbour.GetPieceInTile():
                    continue
                if Neighbour.GetPieceInTile().GetPieceType().upper() == 'S' and (Neighbour.GetPieceInTile().GetPieceType().isupper() == isFirst):
                    Commands.append(self.CreateMoveCommand(Neighbour.GetId(),DefenceTile.GetId()))
                    DefenceTileCoordinatesFilled[DefenceTiles.index(DefenceTile)] = True
                    break
        BaronTile = self.GetOwnBaron(TileList, isFirst)
        for DefenceTile in DefenceTiles:
            if not DefenceTileCoordinatesFilled[DefenceTiles.index(DefenceTile)] and len(Commands) < 2:
                SharedTiles = self.GetTilesNeighbouringTwoTiles(BaronTile, DefenceTile)
                if not SharedTiles:
                    break
                SpawnTile = SharedTiles[0]
                Commands.append(self.CreateSpawnCommand(SpawnTile.GetId()))
                Commands.append(self.CreateMoveCommand(SpawnTile.GetId(),DefenceTile.GetId()))
        return Commands

    def ReturnTileObjectsFromDefenceTileCoordinates(self, DefenceTileCoordinates, TileList):
        return [Tile for DefenceTileCoordinate in DefenceTileCoordinates for Tile in TileList if (Tile.Getx(), Tile.Gety(), Tile.Getz()) == DefenceTileCoordinate]
        '''preserves order of defencetilecoordinates'''

    def ReturnClosestTileInTileListToDesinationTile(self, TileList, DestinationTile):
        MinimumDistance = None
        MinimumDistanceTile = None
        for StartTile in TileList:
            Distance = StartTile.GetDistanceToTileT(DestinationTile)
            if not MinimumDistance:
                MinimumDistance = Distance
                MinimumDistanceTile = StartTile
            if Distance <= MinimumDistance:
                MinimumDistance = Distance
                MinimumDistanceTile = StartTile
        return MinimumDistance, MinimumDistanceTile

    def GetOwnBaron(self, TileList, isFirst):
        MyBaron = 'B' if isFirst else 'b'
        BaronTile = TileList[0]
        for Space in TileList:
            if Space.GetPieceInTile() and Space.GetPieceInTile().GetPieceType() == MyBaron:
                BaronTile = Space
        return BaronTile

    def GetPieceAssociatedWithTerrain(self, Terrain):
        if Terrain == '#':
            return 'less'
        if Terrain == '~':
            return 'pbds'

    def GetTilesNotNeighbouringGivenTiles(self, TileList, Tiles):
        return [Tile for Tile in TileList if Tile not in Tiles and not(bool(set(Tile.GetNeighbours()) & set(Tiles)))]

    def MoveToNewTerrain(self, TileList, isFirst, Terrain, NumberOfMovesLeft):
        if Terrain == '#':
            NonProtectingSerfTiles = self.GetNonProtectingSerfTiles(TileList, isFirst) + [Tile for Tile in self.GetLESSPieces(TileList, isFirst) if Tile.GetTerrain() != '#']
        elif Terrain == '~':
            NonProtectingSerfTiles = self.GetNonProtectingSerfTiles(TileList, isFirst) + [Tile for Tile in self.GetPBDSPieces(TileList, isFirst) if Tile.GetTerrain() != '~']
        Commands = []
        MinimumDistance = None
        MinimumDistanceSerfToTerrainTiles = []
        if not NonProtectingSerfTiles:
            BaronTile = self.GetOwnBaron(TileList, isFirst)
            for Tile in BaronTile.GetNeighbours():
                if not Tile.GetPieceInTile():
                    Commands.append(self.CreateSpawnCommand(Tile.GetId()))
                    NumberOfMovesLeft -= 1
                    #SerfSpawned = True
                    NonProtectingSerfTiles = [Tile]
                    break
        for SerfTile in NonProtectingSerfTiles:
            #TerrainTiles = self.GetTerrainTiles(self.GetDistancedTiles(TileList, isFirst),Terrain) #
            TerrainTiles = self.GetTerrainTiles([Tile for Tile in self.GetTilesNotNeighbouringGivenTiles(TileList, self.DefenceTiles) if not Tile.GetPieceInTile()],Terrain)
            for TerrainTile in TerrainTiles:
                if MinimumDistance == None:
                    MinimumDistance = SerfTile.GetDistanceToTileT(TerrainTile)
                    MinimumDistanceSerfToTerrainTiles = [SerfTile,TerrainTile]
                else:
                    Distance = SerfTile.GetDistanceToTileT(TerrainTile)
                    if Distance < MinimumDistance:
                        MinimumDistance = Distance
                        MinimumDistanceSerfToTerrainTiles = [SerfTile,TerrainTile]
        if MinimumDistance == None or NumberOfMovesLeft == 0:
            return Commands
        TilesToMoveTo = self.MoveToTile(MinimumDistanceSerfToTerrainTiles[0], MinimumDistanceSerfToTerrainTiles[1], MinimumDistance, NumberOfMovesLeft-1)
        StartTile = MinimumDistanceSerfToTerrainTiles[0]
        for Tile in TilesToMoveTo:
            if StartTile.GetId() != Tile.GetId():
                Commands.append(self.CreateMoveCommand(StartTile.GetId(), Tile.GetId()))
            StartTile = Tile
        if StartTile == MinimumDistanceSerfToTerrainTiles[1]:
            PieceAssociatedWithTerrain = self.GetPieceAssociatedWithTerrain(Terrain)
            Commands.append(self.CreateUpgradeCommand(PieceAssociatedWithTerrain, StartTile.GetId()))
            return Commands
        FinalTile = self.MoveToTile(StartTile, MinimumDistanceSerfToTerrainTiles[1], StartTile.GetDistanceToTileT(MinimumDistanceSerfToTerrainTiles[1]), 1)
        if not FinalTile:
            return Commands
        if StartTile.GetId() != FinalTile[0].GetId():
            Commands.append(self.CreateMoveCommand(StartTile.GetId(), FinalTile[0].GetId()))
        return Commands

    def MoveToTile(self, SourceTile, DestinationTile, Distance, NumberOfMovesLeft):
        TilesToMoveTo = []
        if NumberOfMovesLeft > 0 and Distance != 0:
            Change = False
            for Tile in SourceTile.GetNeighbours():
                if not Tile.GetPieceInTile():
                    NewDistance = Tile.GetDistanceToTileT(DestinationTile)
                    if NewDistance < Distance:
                        Change = True
                        TilesToMoveTo.append(Tile)
                        TilesToMoveTo += self.MoveToTile(Tile, DestinationTile, NewDistance, NumberOfMovesLeft-1)
                        break
            if not Change:
                for Tile in SourceTile.GetNeighbours():
                    if not Tile.GetPieceInTile():
                        NewDistance = Tile.GetDistanceToTileT(DestinationTile)
                        if NewDistance <= Distance:
                            TilesToMoveTo.append(Tile)
                            TilesToMoveTo += self.MoveToTile(Tile, DestinationTile, NewDistance, NumberOfMovesLeft-1)
                            break
        elif Distance == 0:
            return [SourceTile]
        return TilesToMoveTo

    def GetTerrainTiles(self, TileList, Terrain):
        return [Tile for Tile in TileList if Tile.GetTerrain() == Terrain]

    def DefenceTilesFilled(self, isFirst):
        for Tile in self.DefenceTiles:
            if not Tile.GetPieceInTile():
                return False
            if Tile.GetPieceInTile().GetPieceType().isupper() != isFirst:
                return False
        return True

    def GetNearestEnemySerfDistanceToBaron(self, TileList, isFirst):
        Distance = self.ReturnClosestTileInTileListToDesinationTile(self.GetSerfPieces(TileList,not(isFirst)),self.GetOwnBaron(TileList, isFirst))
        if Distance:
            return Distance
        else:
            return 1000

    def GetPBDSPiecesInBog(self, TileList, isFirst):
        PBDSPieces = self.GetPBDSPieces(TileList, isFirst)
        return len([Tile for Tile in PBDSPieces if Tile.GetTerrain() == '~'])

    def GetLESSPiecesInForest(self, TileList, isFirst):
        LESSPieces = self.GetLESSPieces(TileList, isFirst)
        return len([Tile for Tile in LESSPieces if Tile.GetTerrain() == '#'])

    def GetCommands(self, TileList, isFirst=True):
        if not self.DefenceTiles:
            self.CreateDefenceTilesAndDefenceTileCoordinates(TileList, isFirst)
        Commands = []
        if not self.DefenceTilesFilled(isFirst):
            Commands += self.CreateProtectingSerfFormation(TileList, isFirst)
        if 1.5*self.GetLumber() > self.GetFuel() or self.GetPBDSPiecesInBog(TileList, isFirst) < self.GetLESSPiecesInForest(TileList, isFirst):
            if self.GetLumber() > (1+2*self.GetGridSize(TileList)) and self.GetFuel() > (2*self.GetGridSize(TileList)-1):
                Commands += self.MoveToNewTerrain(TileList, isFirst, '~', 3-len(Commands))
            else:
                Commands += self.GetMoreFuel(TileList, isFirst, 3-len(Commands))
                Commands += self.MoveToNewTerrain(TileList, isFirst, '~', 3-len(Commands))
        else:
            if self.GetLumber() > (1+2*self.GetGridSize(TileList)) and self.GetFuel() > (2*self.GetGridSize(TileList)-1):
                Commands += self.MoveToNewTerrain(TileList, isFirst, '#', 3-len(Commands))
            else:
                Commands += self.GetMoreLumber(TileList, isFirst, 3-len(Commands))
                Commands += self.MoveToNewTerrain(TileList, isFirst, '#', 3-len(Commands))
        Commands += self.GetMoreFuel(TileList, isFirst, 3-len(Commands))
        Commands += self.GetMoreLumber(TileList, isFirst, 3-len(Commands))
        Commands = Commands[:3]
        return Commands

class SecondAI(Player):
    def GetCommands(self, TileList, isFirst=True):
        MyBaron = 'B' if isFirst else 'b'
        BaronTile = TileList[0]
        for Space in TileList:
            if Space.GetPieceInTile() and Space.GetPieceInTile().GetPieceType() == MyBaron:
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
            if NeighboringTile.GetPieceInTile() and not NeighboringTile.GetId() == MoveOrigin:
                IsBaronSafe = False
            elif not NeighboringTile.GetId() == MoveOrigin:
                SpawnLocales.append(NeighboringTile.GetId())
        if IsBaronSafe:
            SecondCommand = "spawn {0}".format(random.choice(SpawnLocales))
        else:
            SecondCommand = "dig {0}".format(MoveDestination.GetId())
        return ["move {0} {1}".format(MoveOrigin, MoveDestination.GetId()),
                SecondCommand,
                "saw {0}".format(MoveDestination.GetId())]


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
            Player1 = Player(Items[0], int(Items[1]), int(
                Items[2]), int(Items[3]), int(Items[4]))
            LineFromFile = f.readline().rstrip()
            Items = LineFromFile.split(",")
            Player2 = Player(Items[0], int(Items[1]), int(
                Items[2]), int(Items[3]), int(Items[4]))
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
    T = [" ", "#", "#", " ", "~", "~", " ", " ", " ", "~", " ", "#", "#", " ", " ", " ",
         " ", " ", "#", "#", "#", "#", "~", "~", "~", "~", "~", " ", "#", " ", "#", " "]
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


def SetUpRandomGame(ForestProbability=0.3, PeatBogProbability=0.3, MinGridSize=8, MaxGridSize=12, AICount=0):
    # Supply Cap is GridSize - 3
    # Available Lumber and Fuel is between GridSize and double GridSize
    T = [" "]
    GridSize = random.randint((MinGridSize + 1)//2, MaxGridSize//2) * 2 # has to be even
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
            Player1 = FirstAI("AI Player",0, StartingLumber, StartingFuel, SupplyCap)
            Player2 = Player("Human Player",  1, StartingLumber, StartingFuel, SupplyCap)
        else:
            print("Human Player goes first")
            Player1 = Player("Human Player", 0, StartingLumber, StartingFuel, SupplyCap)
            Player2 = FirstAI("AI Player",  1, StartingLumber, StartingFuel, SupplyCap)      
    elif AICount == 2:
        Player1 = FirstAI("AI Player One", 0, StartingLumber, StartingFuel, SupplyCap)
        Player2 = SecondAI("AI Player Two", 1, StartingLumber, StartingFuel, SupplyCap)
    Grid.SetUpGridTerrain(T)
    Grid.AddPiece(True, "Baron", 0)
    Grid.AddPiece(True, "Serf", GridSize)
    Grid.AddPiece(False, "Baron", GridSize * GridSize // 2 - 1)
    Grid.AddPiece(False, "Serf", GridSize * GridSize // 2 - GridSize - 1)
    return Player1, Player2, Grid


def SetUpDefaultGameAgainstAI():
    T = [" ", "#", "#", " ", "~", "~", " ", " ", " ", "~", " ", "#", "#", " ", " ", " ",
         " ", " ", "#", "#", "#", "#", "~", "~", "~", "~", "~", " ", "#", " ", "#", " "]
    AiStarts = random.choice([True, False])
    GridSize = 8
    Grid = HexGrid(GridSize)
    if AiStarts:
        print("AI Player goes first.")
        Player1 = FirstAI("AI Player", 0, 10, 10, 5)
        Player2 = Player("Human Player", 1, 10, 10, 5)
    else:
        print("Human Player goes first")
        Player1 = Player("Human Player", 0, 10, 10, 5)
        Player2 = FirstAI("AI Player", 1, 10, 10, 5)
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
                    SummaryOfResult, FuelChange, LumberChange, SupplyChange = Grid.ExecuteCommand(
                        Items, Player1.GetFuel(), Player1.GetLumber(), Player1.GetPiecesInSupply())
                    Player1.UpdateLumber(LumberChange)
                    Player1.UpdateFuel(FuelChange)
                    if SupplyChange == 1:
                        Player1.RemoveTileFromSupply()
                else:
                    SummaryOfResult, FuelChange, LumberChange, SupplyChange = Grid.ExecuteCommand(
                        Items, Player2.GetFuel(), Player2.GetLumber(), Player2.GetPiecesInSupply())
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
            GameOver, Player1VPsGained, Player2VPsGained = Grid.DestroyPiecesAndCountVPs()
            GameOver = True
        else:
            GameOver, Player1VPsGained, Player2VPsGained = Grid.DestroyPiecesAndCountVPs()
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
