{-# LANGUAGE FlexibleContexts #-}
{-# LANGUAGE BinaryLiterals #-}
{-# LANGUAGE DataKinds #-}
{-# LANGUAGE KindSignatures #-}
{-# LANGUAGE GeneralizedNewtypeDeriving #-}

module Mips where

import CLaSH.Sized.Unsigned (Unsigned)
import CLaSH.Sized.Signed (Signed)
import CLaSH.Sized.Vector (Vec((:>), Nil), (!!), replace, repeat, (++))
import CLaSH.Class.Resize (zeroExtend, extend, resize)
import CLaSH.Sized.BitVector (BitVector, (++#), Bit)
import CLaSH.Class.BitPack (pack, unpack)
import CLaSH.Prelude (slice, fromInteger, negate, shiftL, shiftR, (.&.), (.|.), xor)
import qualified CLaSH.Prelude as P
import CLaSH.Promoted.Nat.Literals as Nat
import CLaSH.Signal (Signal, register, sample)

import Prelude ((+), (-), (*), (==), (<), ($), (.), filter, take, fmap, not, error, Eq, Show, Bool(True,False), Maybe(Just,Nothing))

import Control.DeepSeq (NFData)



type SWord = Signed 32
type UWord = Unsigned 32
newtype RegFile = RegFile (Vec 32 SWord) deriving (Show, NFData)

newtype RegPtr = RegPtr (Unsigned 5)

readRegister :: RegFile -> RegPtr -> SWord
readRegister _ (RegPtr 0) = 0
readRegister (RegFile rf) (RegPtr address) = rf !! address

writeRegister :: RegFile -> RegPtr -> SWord -> RegFile
writeRegister (RegFile rf) (RegPtr address) word = RegFile (replace address word rf)


newtype RAM = RAM (Vec 128 SWord) deriving (Show, NFData)
newtype Ptr = Ptr (Unsigned 32)

readRAM :: RAM -> Ptr -> SWord
readRAM (RAM ram) (Ptr address) = ram !! (shiftR address 2)

writeRAM :: RAM -> Ptr -> SWord -> RAM
writeRAM (RAM rf) (Ptr address) word = RAM (replace (shiftR address 2) word rf)

data Instruction
  -- Rtype
  = Add (RegPtr, RegPtr, RegPtr)
  | Sub (RegPtr, RegPtr, RegPtr)
  | And (RegPtr, RegPtr, RegPtr)
  | Or  (RegPtr, RegPtr, RegPtr)
  | Xor (RegPtr, RegPtr, RegPtr)
  | Nor (RegPtr, RegPtr, RegPtr)
  | Slt (RegPtr, RegPtr, RegPtr)
  -- Itype
  | Beq  (RegPtr, RegPtr, SWord)
  | AddI (RegPtr, RegPtr, SWord)
  | SltI (RegPtr, RegPtr, SWord)
  | AndI (RegPtr, RegPtr, SWord) -- sarebbe unsigned
  | OrI  (RegPtr, RegPtr, SWord) -- sarebbe unsigned
  | XorI (RegPtr, RegPtr, SWord) -- sarebbe unsigned
  -- Memory
  | LoadW  (RegPtr, RegPtr, SWord)
  | StoreW (RegPtr, RegPtr, SWord)
  -- Others
  | Jump (Unsigned 26)
  | Halt -- just for debugging




encodeInstruction :: Instruction -> SWord
encodeInstruction instr = unpack $ case instr of
  -- Rtype
  Add args -> encodeRtype args 0 0b100000
  Sub args -> encodeRtype args 0 0b100010
  And args -> encodeRtype args 0 0b100100
  Or  args -> encodeRtype args 0 0b100101
  Xor args -> encodeRtype args 0 0b100110
  Nor args -> encodeRtype args 0 0b100111
  Slt args -> encodeRtype args 0 0b101010
  -- Itype
  Beq  args -> encodeItype 0b000100 args
  AddI args -> encodeItype 0b001000 args
  SltI args -> encodeItype 0b001010 args
  AndI args -> encodeItype 0b001100 args
  OrI  args -> encodeItype 0b001101 args
  XorI args -> encodeItype 0b001110 args
  -- Memory
  LoadW  args -> encodeItype 0b100011 args
  StoreW args -> encodeItype 0b101011 args
  -- Others
  Jump address -> op 0b000010 ++# pack address
  Halt -> op 0b111111 ++# 0
  otherwise -> error "Cannot encode instruction"
  where
    op x = x :: BitVector 6
    sha x = x :: BitVector 5
    reg (RegPtr r) = pack r :: BitVector 5
    encodeRtype (r1, r2, d) shift funct = op 0 ++# reg r1 ++# reg r2 ++# reg d ++# sha shift ++# op funct
    encodeItype :: BitVector 6 -> (RegPtr, RegPtr, SWord) -> BitVector 32
    encodeItype o (r1, d, imm) = op o ++# reg r1 ++# reg d ++# pack (resize imm)



decodeInstruction :: UWord -> Instruction
decodeInstruction val = case op of
  0b000000 -> case funct of
    0b100000 -> Add (r1, r2, d)
    0b100010 -> Sub (r1, r2, d)
    0b100100 -> And (r1, r2, d)
    0b100101 -> Or  (r1, r2, d)
    0b100110 -> Xor (r1, r2, d)
    0b100111 -> Nor (r1, r2, d)
    0b101010 -> Slt (r1, r2, d)
    otherwise -> error "Cannot decode Rtype instruction"
  -- Itype
  0b000100 -> Beq (r1, r2, extend imm)
  0b001000 -> AddI (r1, r2, extend imm)
  0b001010 -> SltI (r1, r2, extend imm)
  0b001100 -> AndI (r1, r2, zeroExtend imm)
  0b001101 -> OrI (r1, r2, zeroExtend imm)
  0b001110 -> XorI (r1, r2, zeroExtend imm)
  -- Memory
  0b100011 -> LoadW (r1, r2, extend imm)
  0b101011 -> StoreW (r1, r2, extend imm)
  -- Others
  0b000010 -> Jump address
  0b111111 -> Halt
  otherwise -> error "Cannot decode instruction"
  where
    op = slice Nat.d31 Nat.d26 val
    r1 = reg $ slice Nat.d25 Nat.d21 val
    r2 = reg $ slice Nat.d20 Nat.d16 val
    d = reg $ slice Nat.d15 Nat.d11 val
    sha = slice Nat.d10 Nat.d6 val
    funct = slice Nat.d5 Nat.d0 val
    imm = unpack $ slice Nat.d15 Nat.d0 val
    address = unpack $ slice Nat.d25 Nat.d0 val
    reg r = RegPtr $ unpack r


data CPUActivity
  = ExecutingInstruction
  | Halted

newtype PC = PC UWord
data CPUState = CPUState CPUActivity RegFile PC

signedToUnsigned :: SWord -> UWord
signedToUnsigned = P.bitCoerce

unsignedToSigned :: UWord -> SWord
unsignedToSigned = P.bitCoerce

cycle :: (CPUState, RAM, RAM) -> (CPUState, RAM, RAM)
cycle (CPUState activity registers (PC pc), rom, ram) = case activity of
  ExecutingInstruction -> case instr of
    -- Rtype
    Add (r1, r2, d) -> (CPUState ExecutingInstruction registers' (PC pc4), rom, ram)
      where
        result = readReg r1 + readReg r2
        registers' = writeReg d result
    Sub (r1, r2, d) -> (CPUState ExecutingInstruction registers' (PC pc4), rom, ram)
      where
        result = readReg r1 - readReg r2
        registers' = writeReg d result
    And (r1, r2, d) -> (CPUState ExecutingInstruction registers' (PC pc4), rom, ram)
      where
        result = readReg r1 .&. readReg r2
        registers' = writeReg d result
    Or (r1, r2, d) -> (CPUState ExecutingInstruction registers' (PC pc4), rom, ram)
      where
        result = readReg r1 .|. readReg r2
        registers' = writeReg d result
    Xor (r1, r2, d) -> (CPUState ExecutingInstruction registers' (PC pc4), rom, ram)
      where
        result = readReg r1 `xor` readReg r2
        registers' = writeReg d result
    Nor (r1, r2, d) -> (CPUState ExecutingInstruction registers' (PC pc4), rom, ram)
      where
        result = negate $ readReg r1 .|. readReg r2
        registers' = writeReg d result
    Slt (r1, r2, d) -> (CPUState ExecutingInstruction registers' (PC pc4), rom, ram)
      where
        result = if readReg r1 < readReg r2 then 1 else 0
        registers' = writeReg d result
    -- Itype
    Beq (r1, r2, simm) -> (CPUState ExecutingInstruction registers (PC pc_jump), rom, ram)
      where
        eimm = extend simm :: SWord
        pc' = pc4 + (signedToUnsigned $ shiftL eimm 2)
        pc_jump = if readReg r1 == readReg r2 then pc' else pc4
    AddI (r1, d, simm) -> (CPUState ExecutingInstruction registers' (PC pc4), rom, ram)
      where
        eimm = extend simm :: SWord
        result = readReg r1 + eimm
        registers' = writeReg d result
    SltI (r1, d, simm) -> (CPUState ExecutingInstruction registers' (PC pc4), rom, ram)
      where
        eimm = extend simm :: SWord
        result = if readReg r1 < eimm then 1 else 0
        registers' = writeReg d result
    AndI (r1, d, imm) -> (CPUState ExecutingInstruction registers' (PC pc4), rom, ram)
      where
        result = readReg r1 .&. imm
        registers' = writeReg d result
    OrI (r1, d, imm) -> (CPUState ExecutingInstruction registers' (PC pc4), rom, ram)
      where
        result = readReg r1 .|. imm
        registers' = writeReg d result
    XorI (r1, d, imm) -> (CPUState ExecutingInstruction registers' (PC pc4), rom, ram)
      where
        result = readReg r1 `xor` imm
        registers' = writeReg d result
    -- Memory
    LoadW (r1, d, simm) -> (CPUState ExecutingInstruction registers' (PC pc4), rom, ram)
      where
        eimm = extend simm :: SWord
        addr = signedToUnsigned $ readReg r1 + eimm
        registers' = writeReg d (readRAM ram (Ptr addr))
    StoreW (r1, r2, simm) -> (CPUState ExecutingInstruction registers (PC pc4), rom, ram')
      where
        eimm = extend simm :: SWord
        addr = signedToUnsigned $ readReg r1 + eimm
        ram' = writeRAM ram (Ptr addr) (readReg r2)
    -- Others
    Jump dest -> (CPUState ExecutingInstruction registers (PC pc_jump), rom, ram)
      where
        dest' = extend dest :: Unsigned 28
        dest'' = pack $ shiftL dest' 2
        pc_jump = unpack ((slice Nat.d31 Nat.d28 pc4) ++# dest'')
    Halt -> (CPUState Halted registers (PC pc), rom, ram)
    where
      readReg r = readRegister registers r
      writeReg d val = writeRegister registers d val
      pc4 = pc + 4
      loadedWord = readRAM rom (Ptr pc)
      instr = decodeInstruction (signedToUnsigned loadedWord)

  Halted -> (CPUState Halted registers (PC pc), rom, ram)
  otherwise -> error "bottom"



isHalted :: CPUState -> Bool
isHalted (CPUState Halted _ _) = True
isHalted _ = False


cpuHardware :: CPUState -> RAM -> RAM -> Signal (Bool, RegFile, RAM)
cpuHardware initialCPUState rom ram = outputSignal
  where
    systemState = register (initialCPUState, rom, ram) systemState'
    systemState' = fmap cycle systemState
    getOutput :: (CPUState, RAM, RAM) -> (Bool, RegFile, RAM)
    getOutput (state, _, i_ram) = (isHalted state, get_rf state, i_ram)
      where
        get_rf :: CPUState -> RegFile
        get_rf (CPUState _ rf _) = rf
    outputSignal = fmap getOutput systemState'

defaultCPUState :: CPUState
defaultCPUState = CPUState ExecutingInstruction (RegFile (repeat 0 :: Vec 32 SWord)) (PC 0)

simpleProgram =
  AddI (rr 0, rr 2, 5) :>
  AddI (rr 0, rr 3, 12) :>
  AddI (rr 3, rr 7, -9) :>
  Or (rr 7, rr 2, rr 4) :>
  And (rr 3, rr 4, rr 5) :>
  Add (rr 5, rr 4, rr 5) :>
  Beq (rr 5, rr 7, 10) :>
  Slt (rr 3, rr 4, rr 4) :>
  Beq (rr 4, rr 0, 1) :>
  AddI (rr 0, rr 5, 0) :>
  Slt (rr 7, rr 2, rr 4) :>
  Add (rr 4, rr 5, rr 7) :>
  Sub (rr 7, rr 2, rr 7) :>
  StoreW (rr 3, rr 7, 68) :>
  LoadW (rr 0, rr 2, 80) :>
  Jump 17 :>
  AddI (rr 0, rr 2, 1) :>
  StoreW (rr 0, rr 2, 84) :>
  Halt :>
  Nil
  where
    rr x = RegPtr x

ram_mem :: Vec 128 SWord
ram_mem = repeat 0

rom_mem :: Vec 128 SWord
rom_mem = fmap encodeInstruction simpleProgram ++ (repeat 0xffffffff)

simpleProgramCPU :: Signal (Bool, RegFile, RAM)
simpleProgramCPU = cpuHardware defaultCPUState (RAM rom_mem) (RAM ram_mem)

simpleProgramOutput :: [(Bool, RegFile, RAM)]
simpleProgramOutput = take 1 $ filter (\(h, _, _) -> h == True) $ sample simpleProgramCPU

run_hw p = P.mapM_ P.print p
