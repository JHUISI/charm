/*
 * RELIC is an Efficient LIbrary for Cryptography
 * Copyright (C) 2007-2012 RELIC Authors
 *
 * This file is part of RELIC. RELIC is legal property of its developers,
 * whose names are not listed here. Please refer to the COPYRIGHT file
 * for contact information.
 *
 * RELIC is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * RELIC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with RELIC. If not, see <http://www.gnu.org/licenses/>.
 */

/**
 * @file
 *
 * Project configuration.
 *
 * @version $Id: relic_conf.h.in 45 2009-07-04 23:45:48Z dfaranha $
 * @ingroup relic
 */

#ifndef RELIC_CONF_H
#define RELIC_CONF_H

/** Project version. */
#define VERSION "0.3.4"

/** Debugging support. */
/* #undef DEBUG */
/** Profiling support. */
/* #undef PROFL */
/** Error handling support. */
/* #undef CHECK */
/** Verbose error messages. */
#define VERBS
/** Trace support. */
/* #undef TRACE */
/** Multithreading. */
/* #undef MULTI */
/** Build documentation. */
#define DOCUM
/** Build only the selected algorithms. */
/* #undef STRIP */
/** Build with printing disabled. */
/* #undef QUIET */
/** Build with colored output. */
#define COLOR
/** Build with big-endian support. */
/* #undef BIGED */
/** Build shared library. */
#define SHLIB
/** Build static library. */
#define STLIB
/** Build with multithreading support. */
/* #undef MULTI */

/** Number of times each test is ran. */
#define TESTS    0
/** Number of times each benchmark is ran. */
#define BENCH    0

/** Number of available cores. */
#define CORES    1

/** Generic architecture. */
#define NONE     1
/** Atmel AVR ATMega128 8-bit architecture. */
#define AVR      2
/** MSP430 16-bit architecture. */
#define MSP      3
/** ARM 32-bit architecture. */
#define ARM      4
/** Intel x86-compatible 32-bit architecture. */
#define X86      5
/** AMD64-compatible 64-bit architecture. */
#define X86_64	 6 
/** Architecture. */
#define ARCH	 X86_64

/** Size of word in this architecture. */
#define WORD     64

/** Byte boundary to align digit vectors. */
#define ALIGN    1

/** Build multiple precision integer module. */
#define WITH_BN
/** Build prime field module. */
#define WITH_FP
/** Build binary field module. */
#define WITH_FB
/** Build ternary field module. */
#define WITH_FT
/** Build prime elliptic curve module. */
#define WITH_EP
/** Build binary elliptic curve module. */
#define WITH_EB
/** Build elliptic curve cryptography module. */
#define WITH_EC
/** Build hyperelliptic curve cryptography module. */
#define WITH_HB
/** Build pairings over prime curves module. */
#define WITH_PP
/** Build pairings over binary curves module. */
#define WITH_PB
/** Build pairing-based cryptography module. */
#define WITH_PC
/** Build hash functions. */
#define WITH_MD
/** Build cryptographic protocols. */
#define WITH_CP

/** Easy C-only backend. */
#define EASY	 1
/** GMP backend. */
#define GMP      2
/** Arithmetic backend. */
#define ARITH    EASY

/** Required precision in bits. */
#define BN_PRECI 256
/** A multiple precision integer can store w words. */
#define SINGLE	 0
/** A multiple precision integer can store the result of an addition. */
#define CARRY	 1
/** A multiple precision integer can store the result of a multiplication. */
#define DOUBLE	 2
/** Effective size of a multiple precision integer. */
#define BN_MAGNI DOUBLE
/** Number of Karatsuba steps. */
#define BN_KARAT 0

/** Multiple precision arithmetic method */
#define BN_METHD "COMBA;COMBA;MONTY;SLIDE;BASIC;BASIC"

/** Schoolbook multiplication. */
#define BASIC    1
/** Comba multiplication. */
#define COMBA    2
/** Chosen multiple precision multiplication method. */
#define BN_MUL   COMBA

/** Schoolbook squaring. */
#define BASIC    1
/** Comba squaring. */
#define COMBA    2
/** Reuse multiplication for squaring. */
#define MULTP    4
/** Chosen multiple precision multiplication method. */
#define BN_SQR   COMBA

/** Division modular reduction. */
#define BASIC    1
/** Barrett modular reduction. */
#define BARRT    2
/** Montgomery modular reduction. */
#define MONTY    3
/** Pseudo-Mersenne modular reduction. */
#define PMERS    4
/** Chosen multiple precision modular reduction method. */
#define BN_MOD   MONTY

/** Binary modular exponentiation. */
#define BASIC    1
/** Sliding window modular exponentiation. */
#define SLIDE    2
/** Constant-time Montgomery powering ladder. */
#define MONTY    3
/** Chosen multiple precision modular exponentiation method. */
#define BN_MXP   SLIDE

/** Basic Euclidean GCD Algorithm. */ 
#define BASIC    1
/** Lehmer's fast GCD Algorithm. */
#define LEHME    2
/** Stein's binary GCD Algorithm. */
#define STEIN    3
/** Chosen multiple precision greatest common divisor method. */
#define BN_GCD   BASIC

/** Basic prime generation. */
#define BASIC    1
/** Safe prime generation. */
#define SAFEP    2
/** Strong prime generation. */
#define STRON    3
/** Chosen prime generation algorithm. */
#define BN_GEN   BASIC

/** Prime field size in bits. */
#define FP_PRIME 256
/** Number of Karatsuba steps. */
#define FP_KARAT 0
/** Prefer Pseudo-Mersenne primes over random primes. */
/* #undef FP_PMERS */
/** Use -1 as quadratic non-residue. */ 
/* #undef FP_QNRES */
/** Width of window processing for exponentiation methods. */
#define FP_WIDTH 4

/** Prime field arithmetic method */
#define FP_METHD "BASIC;COMBA;COMBA;MONTY;LOWER;MONTY"

/** Schoolbook addition. */
#define BASIC    1
/** Integrated modular addtion. */
#define INTEG    3
/** Chosen prime field multiplication method. */
#define FP_ADD   BASIC

/** Schoolbook multiplication. */
#define BASIC    1
/** Comba multiplication. */
#define COMBA    2
/** Integrated modular multiplication. */
#define INTEG    3
/** Chosen prime field multiplication method. */
#define FP_MUL   COMBA

/** Schoolbook squaring. */
#define BASIC    1
/** Comba squaring. */
#define COMBA    2
/** Integrated modular squaring. */
#define INTEG    3
/** Reuse multiplication for squaring. */
#define MULTP    4
/** Chosen prime field multiplication method. */
#define FP_SQR   COMBA

/** Division-based reduction. */
#define BASIC    1
/** Fast reduction modulo special form prime. */
#define QUICK    2
/** Montgomery modular reduction. */
#define MONTY    3
/** Chosen prime field reduction method. */
#define FP_RDC   MONTY

/** Inversion by Fermat's Little Theorem. */
#define BASIC    1
/** Binary inversion. */
#define BINAR    2
/** Integrated modular multiplication. */
#define MONTY    3
/** Extended Euclidean algorithm. */
#define EXGCD    4
/** Use implementation provided by the lower layer. */
#define LOWER    6
/** Chosen prime field inversion method. */ 
#define FP_INV   LOWER 

/** Binary modular exponentiation. */
#define BASIC    1
/** Sliding window modular exponentiation. */
#define SLIDE    2
/** Constant-time Montgomery powering ladder. */
#define MONTY    3
/** Chosen multiple precision modular exponentiation method. */
#define FP_EXP   MONTY

/** Irreducible polynomial size in bits. */
#define FB_POLYN 283
/** Number of Karatsuba steps. */
#define FB_KARAT 0
/** Prefer trinomials over pentanomials. */
#define FB_TRINO
/** Prefer square-root friendly polynomials. */
/* #undef FB_SQRTF */
/** Precompute multiplication table for sqrt(z). */
#define FB_PRECO
/** Width of window processing for exponentiation methods. */
#define FB_WIDTH 4

/** Binary field arithmetic method */
#define FB_METHD "LODAH;TABLE;QUICK;QUICK;QUICK;QUICK;EXGCD;SLIDE;QUICK"

/** Shift-and-add multiplication. */
#define BASIC    1
/** Lopez-Dahab multiplication. */
#define LODAH	 2
/** Integrated modular multiplication. */
#define INTEG	 3
/** Left-to-right Comb multiplication. */
#define LCOMB	 4
/** Right-to-left Comb multiplication. */
#define RCOMB	 5
/** Chosen binary field multiplication method. */
#define FB_MUL   LODAH

/** Basic squaring. */
#define BASIC    1
/** Table-based squaring. */
#define TABLE    2
/** Integrated modular squaring. */
#define INTEG	 3
/** Chosen binary field squaring method. */
#define FB_SQR   TABLE

/** Shift-and-add modular reduction. */
#define BASIC    1
/** Fast reduction modulo a trinomial or pentanomial. */
#define QUICK	 2
/** Chosen binary field modular reduction method. */
#define FB_RDC   QUICK

/** Square root by repeated squaring. */
#define BASIC    1
/** Fast square root extraction. */
#define QUICK	 2
/** Chosen binary field modular reduction method. */
#define FB_SRT   QUICK

/** Trace by repeated squaring. */
#define BASIC    1
/** Fast trace computation. */
#define QUICK	 2
/** Chosen trace computation method. */
#define FB_TRC   QUICK

/** Solve by half-trace computation. */
#define BASIC    1
/** Solve with precomputed half-traces. */
#define QUICK	 2
/** Chosen method to solve a quadratic equation. */
#define FB_SLV   QUICK

/** Inversion by Fermat's Little Theorem. */
#define BASIC    1
/** Binary inversion. */
#define BINAR    2
/** Almost inverse algorithm. */
#define ALMOS    3
/** Extended Euclidean algorithm. */
#define EXGCD    4
/** Itoh-Utsji inversion. */
#define ITOHT    5
/** Use implementation provided by the lower layer. */
#define LOWER    6
/** Chosen binary field inversion method. */
#define FB_INV   EXGCD 

/** Binary modular exponentiation. */
#define BASIC    1
/** Sliding window modular exponentiation. */
#define SLIDE    2
/** Constant-time Montgomery powering ladder. */
#define MONTY    3
/** Chosen multiple precision modular exponentiation method. */
#define FB_EXP   SLIDE

/** Iterated squaring/square-root by consecutive squaring/square-root. */
#define BASIC    1
/** Iterated squaring/square-root by table-based method. */
#define QUICK	 2
/** Chosen method to solve a quadratic equation. */
#define FB_ITR   QUICK

/** Irreducible polynomial size in bits. */
#define FT_POLYN 509
/** Number of Karatsuba steps. */
#define FT_KARAT 0
/** Prefer trinomials over pentanomials. */
#define FT_TRINO
/** Precompute multiplication table for cbrt(z). */
#define FT_PRECO

/** Ternary field arithmetic method */
#define FT_METHD "LODAH;TABLE;QUICK;BASIC;EXGCD"

/** Shift-and-add multiplication. */
#define BASIC    1
/** Lopez-Dahab multiplication. */
#define LODAH	 2
/** Integrated modular multiplication. */
#define INTEG	 3
/** Chosen ternary field multiplication method. */
#define FT_MUL   LODAH

/** Basic cubing. */
#define BASIC    1
/** Table-based cubing. */
#define TABLE    2
/** Integrated modular cubing. */
#define INTEG	 3
/** Chosen ternary field cubing method. */
#define FT_CUB   TABLE

/** Shift-and-add modular reduction. */
#define BASIC    1
/** Fast reduction modulo a trinomial or pentanomial. */
#define QUICK	 2
/** Chosen ternary field modular reduction method. */
#define FT_RDC   QUICK

/** Square root by repeated cubing. */
#define BASIC    1
/** Fast cube root extraction. */
#define QUICK	 2
/** Chosen binary field modular reduction method. */
#define FT_CRT   BASIC

/** Support for ordinary curves. */
#define EP_ORDIN
/** Support for supersingular curves. */
#define EP_SUPER
/** Support for prime curves with efficient endormorphisms. */
#define EP_KBLTZ
/** Use mixed coordinates. */
#define EP_MIXED
/** Build precomputation table for generator. */
#define EP_PRECO
/** Width of precomputation table for fixed point methods. */
#define EP_DEPTH 4
/** Width of window processing for unknown point methods. */
#define EP_WIDTH 4

/** Prime elliptic curve arithmetic method. */
#define EP_METHD "BASIC;LWNAF;COMBS;INTER"

/** Affine coordinates. */
#define BASIC	 1
/** López-Dahab Projective coordinates. */
#define PROJC	 2
/** Chosen binary elliptic curve coordinate method. */
#define EP_ADD	 BASIC

/** Affine coordinates. */
#define BASIC	 1
/** López-Dahab Projective coordinates. */
#define PROJC	 2
/** Chosen binary elliptic curve coordinate method. */
#define EB_ADD	 PROJC

/** Binary point multiplication. */ 
#define BASIC	 1
/** Sliding window. */ 
#define SLIDE    2
/** Montgomery powering ladder. */
#define MONTY	 3
/** Left-to-right Width-w NAF. */ 
#define LWNAF	 4
/** Chosen prime elliptic curve point multiplication method. */
#define EP_MUL	 LWNAF

/** Binary point multiplication. */ 
#define BASIC	 1
/** Yao's windowing method. */
#define YAOWI	 2
/** NAF windowing method. */ 
#define NAFWI	 3
/** Left-to-right Width-w NAF. */ 
#define LWNAF	 4
/** Single-table comb method. */
#define COMBS	 5
/** Double-table comb method. */
#define COMBD    6
/** Chosen prime elliptic curve point multiplication method. */
#define EP_FIX	 COMBS

/** Basic simultaneouns point multiplication. */
#define BASIC    1
/** Shamir's trick. */
#define TRICK    2
/** Interleaving of w-(T)NAFs. */
#define INTER    3
/** Joint sparse form. */
#define JOINT    4
/** Chosen prime elliptic curve simulteanous point multiplication method. */
#define EP_SIM   INTER 

/** Support for ordinary curves. */
#define EB_ORDIN
/** Support for supersingular curves. */
#define EB_SUPER
/** Support for Koblitz anomalous binary curves. */
#define EB_KBLTZ
/** Use mixed coordinates. */
#define EB_MIXED
/** Build precomputation table for generator. */
#define EB_PRECO
/** Width of precomputation table for fixed point methods. */
#define EB_DEPTH 4
/** Width of window processing for unknown point methods. */
#define EB_WIDTH 4

/** Binary elliptic curve arithmetic method. */
#define EB_METHD "PROJC;LWNAF;COMBS;INTER"

/** Affine coordinates. */
#define BASIC	 1
/** López-Dahab Projective coordinates. */
#define PROJC	 2
/** Chosen binary elliptic curve coordinate method. */
#define EB_ADD	 PROJC

/** Binary point multiplication. */ 
#define BASIC	 1
/** López-Dahab point multiplication. */
#define LODAH	 2
/** Halving. */
#define HALVE    3
/** Left-to-right width-w (T)NAF. */ 
#define LWNAF	 4
/** Right-to-left width-w (T)NAF. */ 
#define RWNAF	 5
/** Chosen binary elliptic curve point multiplication method. */
#define EB_MUL	 LWNAF

/** Binary point multiplication. */ 
#define BASIC	 1
/** Yao's windowing method. */
#define YAOWI	 2
/** NAF windowing method. */ 
#define NAFWI	 3
/** Left-to-right Width-w NAF. */ 
#define LWNAF	 4
/** Single-table comb method. */
#define COMBS	 5
/** Double-table comb method. */
#define COMBD    6
/** Chosen binary elliptic curve point multiplication method. */
#define EB_FIX	 COMBS

/** Basic simultaneouns point multiplication. */
#define BASIC    1
/** Shamir's trick. */
#define TRICK    2
/** Interleaving of w-(T)NAFs. */
#define INTER    3
/** Joint sparse form. */
#define JOINT    4
/** Chosen binary elliptic curve simulteanous point multiplication method. */
#define EB_SIM   INTER 

/** Prefer Koblitz anomalous (binary or prime) curves. */
#define EC_KBLTZ

/** Chosen elliptic curve cryptography method. */
#define EC_METHD "PRIME"

/** Prime curves. */
#define PRIME    1
/** Binary curves. */
#define CHAR2    2
/** Chosen elliptic curve type. */
#define EC_CUR	 PRIME

/** Support for supersingular curves. */
#define HB_SUPER
/** Build precomputation table for generator. */
#define HB_PRECO
/** Width of precomputation table for fixed point methods. */
#define HB_DEPTH 4
/** Width of window processing for unknown point methods. */
#define HB_WIDTH 4

/** Binary elliptic curve arithmetic method. */
#define HB_METHD "BASIC;OCTUP;COMBS;INTER"

/** Affine coordinates. */
#define BASIC	 1
/** López-Dahab Projective coordinates. */
#define PROJC	 2
/** Chosen binary elliptic curve coordinate method. */
#define HB_ADD	 PROJC

/** Binary point multiplication. */ 
#define BASIC	 1
/** Left-to-right Width-w NAF. */ 
#define LWNAF	 4
/** Octupling-based windowing. */
#define OCTUP	 7
/** Chosen binary hyperelliptic curve point multiplication method. */
#define HB_MUL	 OCTUP

/** Binary point multiplication. */ 
#define BASIC	 1
/** Yao's windowing method. */
#define YAOWI	 2
/** NAF windowing method. */ 
#define NAFWI	 3
/** Left-to-right Width-w NAF. */ 
#define LWNAF	 4
/** Single-table comb method. */
#define COMBS	 5
/** Double-table comb method. */
#define COMBD    6
/** Yao's windowing method. */
#define OCTUP	 7
/** Chosen binary hyperelliptic curve point multiplication method. */
#define HB_FIX	 COMBS

/** Basic simultaneouns point multiplication. */
#define BASIC    1
/** Shamir's trick. */
#define TRICK    2
/** Interleaving of w-(T)NAFs. */
#define INTER    3
/** Joint sparse form. */
#define JOINT    4
/** Chosen binary elliptic curve simulteanous point multiplication method. */
#define HB_SIM   INTER 

/** Bilinear pairing method. */
#define PP_METHD "INTEG;INTEG;LAZYR;OATEP"

/** Basic quadratic extension field arithmetic. */
#define BASIC    1
/** Integrated extension field arithmetic. */
#define INTEG    3
/* Chosen extension field arithmetic method. */
#define PP_QDR   INTEG 

/** Basic cubic extension field arithmetic. */
#define BASIC    1
/** Integrated extension field arithmetic. */
#define INTEG    3
/* Chosen extension field arithmetic method. */
#define PP_CBC   INTEG 

/** Basic quadratic extension field arithmetic. */
#define BASIC    1
/** Lazy-reduced extension field arithmetic. */
#define LAZYR    2
/* Chosen extension field arithmetic method. */
#define PP_EXT   LAZYR 

/** Parallel implementation. */
/* #undef PP_PARAL */

/** Tate pairing. */
#define TATEP    1
/** Weil pairing. */
#define WEILP    2
/** Optimal ate pairing. */
#define OATEP    3
/** Beta Weil pairing. */
#define BWEIL    4
/** Chosen pairing method over prime elliptic curves. */
#define PP_MAP   OATEP

/** Parallel implementation. */
/* #undef PB_PARAL */

/** Bilinear pairing method. */
#define PB_METHD "ETATS"

/** Pairing computation in genus 1 curves with square roots. */ 
#define ETATS    1
/** Pairing computation in genus 1 curves without square roots. */
#define ETATN    2
/** Pairing computation in genus 2 curves. */
#define ETAT2    3
/** Optimal pairing computation in genus 2 curves. */
#define OETA2    4
/** Chosen binary elliptic curve point pairing method. */
#define PB_MAP	 ETATS

/** Binary elliptic curve arithmetic method. */
#define PC_METHD "PRIME"

/** Prime curves. */
#define PRIME	 1
/** Binary curves. */
#define CHAR2	 2
/** Chosen elliptic curve type. */
#define PC_CUR	 PRIME

/** Choice of hash function. */
#define MD_METHD "SH256"

/** SHA-1 hash function. */
#define SHONE    1
/** SHA-224 hash function. */
#define SH224    2
/** SHA-256 hash function. */
#define SH256    3
/** SHA-384 hash function. */
#define SH384    4
/** SHA-512 hash function. */
#define SH512    5
/** Chosen hash function. */
#define MD_MAP   SH256

/** RSA without padding. */
#define BASIC    1
/** RSA PKCS#1 v1.5 padding. */
#define PKCS1    2
/** RSA PKCS#1 v2.1 padding. */
#define PKCS2    3
/** Chosen RSA padding method. */
#define CP_RSAPD PKCS1

/** Slow RSA decryption/signature. */
#define BASIC    1
/** Fast RSA decryption/signature with CRT. */
#define QUICK    2
/** Chosen RSA method. */
#define CP_RSA   QUICK

/** Standard ECDSA. */
#define BASIC    1
/** ECDSA with fast verification. */
#define QUICK    2
/** Chosen ECDSA method. */
#define CP_ECDSA 

/** Automatic memory allocation. */
#define AUTO     1
/** Static memory allocation. */
#define	STATIC   2
/** Dynamic memory allocation. */
#define DYNAMIC  3
/** Stack memory allocation. */
#define STACK    4
/** Chosen memory allocation policy. */
#define ALLOC    DYNAMIC

/** FIPS 186-2 generator. */
#define FIPS     1
/** Chosen random generator. */
#define RAND     FIPS

/** Null seed. */
#define	ZERO     1
/** Standard C library generator. */
#define LIBC     2
/** Device node generator. */
#define DEV      3
/** Device node generator. */
#define UDEV     4
/** Use Windows' CryptGenRandom. */
#define WCGR     5
/** Chosen random generator seeder. */
#define SEED     DEV

/** Undefined/No operating system. */
#define NONE     1
/** GNU/Linux operating system. */
#define LINUX    2
/** FreeBSD operating system. */
#define FREEBSD  3
/** Windows operating system. */
#define MACOSX   4
/** Windows operating system. */
#define WINDOWS  5
/** Android operating system. */
#define DROID    6
/** Detected operation system. */
#define OPSYS    NONE

/** No timer. */
#define NONE     1
/** Per-process high-resolution timer. */
#define HREAL    2
/** Per-process high-resolution timer. */
#define HPROC    3
/** Per-thread high-resolution timer. */
#define HTHRD    4
/** POSIX-compatible timer. */
#define POSIX    5
/** ANSI-compatible timer. */
#define ANSI     6
/** Cycle-counting timer. */
#define CYCLE    7
/** Chosen timer. */
#define TIMER    ANSI

#ifndef ASM

/**
 * Prints the project options selected at build time.
 */
void conf_print(void);

#endif /* ASM */

#endif /* !RELIC_CONF_H */
