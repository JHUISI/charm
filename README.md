Charm
=====

| Branch      | Status                                                                                                          |
| ----------- | --------------------------------------------------------------------------------------------------------------- |
| `dev`       | [![Build Status](https://travis-ci.org/JHUISI/charm.svg?branch=dev)](https://travis-ci.org/JHUISI/charm)        |
| `dev-2.7`   | [![Build Status](https://travis-ci.org/JHUISI/charm.svg?branch=2.7-dev)](https://travis-ci.org/JHUISI/charm)    |

Charm is a framework for rapidly prototyping advanced cryptosystems.  Based on the Python language, it was designed from the ground up to minimize development time and code complexity while promoting the reuse of components.

Charm uses a hybrid design: performance intensive mathematical operations are implemented in native C modules, while cryptosystems themselves are written in a readable, high-level language.  Charm additionally provides a number of new components to facilitate the rapid development of new schemes and protocols.

Features of Charm include:
* Support for various mathematical settings, including integer rings/fields, bilinear and non-bilinear Elliptic Curve groups
* Base crypto library, including symmetric encryption schemes, hash functions, PRNGs   
* Standard APIs for constructions such as digital signature, encryption, commitments
* A “protocol engine” to simplify the process of implementing multi-party protocols
* An integrated compiler for interactive and non-interactive ZK proofs
* Integrated benchmarking capability

Documentation
=============
For complete install, see our [documentation](https://jhuisi.github.io/charm/install_source.html). 

Pull Requests
=============

We welcome and encourage scheme contributions. If you'd like your scheme implementation included in the Charm distribution, please note a few things.
Schemes in the dev branch are Python 3.x only and ones in the 2.7-dev branch are Python 2.x. For your scheme to be included in unit tests (`make test`), you must include a doctest at a minimum (see schemes in the charm/schemes directory). 

Schemes
=======
We have provided several cryptographic scheme [examples](https://jhuisi.github.io/charm/schemes.html) to get you going. If this doesn't help, then feel free to reach us for questions and/or comments at support@charm-crypto.com.

If you're using Charm to implement schemes, we want to know what your experience is with our framework. Your feedback is very valuable to us! 

Quick Install & Test
====================
Installing Charm from source is straightforward. First, verify that you have installed the following dependencies:
* [GMP 5.x](http://gmplib.org/)
* [PBC](http://crypto.stanford.edu/pbc/download.html) 
* [OPENSSL](http://www.openssl.org/source/)

After that, you may proceed to install a basic configuration of Charm as follows:

* `./configure.sh` (include `--enable-darwin` if running Mac OS X)
* `make install` (may require super-user privileges)
* `make test` (may also require super-user privileges)

If most (or all) Python tests pass, then the Charm installation was successful. Enjoy!

Licensing
=========

Charm is released under an LGPL version 3 license due to libraries that we build on. See the `LICENSE.txt` for details.
