# This fixes an issue where certain python interpeters/operating systems
# fail to properly load shared modules that c extensions depend on.
# In this case, the benchmark module is not handeled properly on osx
# as such we import it preimptively to force its symbols to be loaded. 
import charm.core.benchmark 
