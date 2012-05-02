import miraclbench2
import relicbench


global curve, param_id
library = "relic" # or "relic"

if library == "miracl":
   curve = miraclbench2.benchmarks
   param_id  = miraclbench2.key # pairing-friendly curve over a extension field (prime-based)
elif library == "relic":
   curve = relicbench.benchmarks
   param_id  = relicbench.key # pairing-friendly curve over a extension field (prime-based)
