ABEnumeric - Numeric Attribute Encoding
=======================================

.. module:: charm.toolbox.ABEnumeric
   :synopsis: Numeric attribute encoding for CP-ABE using the bag-of-bits technique

This module implements the "bag of bits" technique from the Bethencourt-Sahai-Waters
CP-ABE paper (IEEE S&P 2007) for representing numeric attributes and comparisons.

Overview
--------

Traditional ABE policies use string attributes like ``ADMIN`` or ``DEPARTMENT_HR``.
This module extends ABE to support numeric comparisons like ``age >= 21`` or ``level > 5``.

The technique converts numeric comparisons into boolean attribute expressions that can
be evaluated using standard ABE schemes.

Quick Start
-----------

.. code-block:: python

    from charm.toolbox.ABEnumeric import NumericAttributeHelper
    from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
    from charm.toolbox.pairinggroup import PairingGroup
    
    # Setup
    group = PairingGroup('SS512')
    cpabe = CPabe_BSW07(group)
    helper = NumericAttributeHelper(num_bits=8)
    
    # Encryption with numeric policy
    policy = helper.expand_policy("age >= 21 and department == 5")
    # ... use expanded policy with cpabe.encrypt()
    
    # Key generation with numeric attributes
    user_attrs = helper.user_attributes({'age': 25, 'department': 5})
    # ... use user_attrs with cpabe.keygen()

Supported Operators
-------------------

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Operator
     - Example
     - Description
   * - ``>=``
     - ``age >= 21``
     - Greater than or equal
   * - ``>``
     - ``level > 5``
     - Greater than
   * - ``<=``
     - ``priority <= 3``
     - Less than or equal
   * - ``<``
     - ``score < 100``
     - Less than
   * - ``==``
     - ``department == 7``
     - Equality

NumericAttributeHelper Class
----------------------------

.. autoclass:: NumericAttributeHelper
   :members:
   :undoc-members:
   :show-inheritance:

Negation Support
----------------

**Important**: The underlying Monotone Span Program (MSP) used in ABE schemes does
NOT support logical negation. This is a fundamental cryptographic limitation.

The PolicyParser's ``!`` prefix creates an attribute with ``!`` in its name, but this
is NOT logical negation.

**Workaround**: Use equivalent expressions:

.. list-table::
   :header-rows: 1
   :widths: 40 40

   * - Negated Expression
     - Equivalent Positive Form
   * - ``NOT (age >= 21)``
     - ``age < 21``
   * - ``NOT (age > 21)``
     - ``age <= 21``
   * - ``NOT (age <= 21)``
     - ``age > 21``
   * - ``NOT (age < 21)``
     - ``age >= 21``
   * - ``NOT (age == 21)``
     - ``(age < 21) or (age > 21)``

Helper Functions
^^^^^^^^^^^^^^^^

.. autofunction:: negate_comparison

.. autofunction:: negate_comparison_to_policy

Example:

.. code-block:: python

    from charm.toolbox.ABEnumeric import negate_comparison, negate_comparison_to_policy
    
    # Convert NOT (age >= 21) to equivalent
    result = negate_comparison('age', '>=', 21)
    # Returns: ('age', '<', 21)
    
    # Get as policy string
    policy = negate_comparison_to_policy('age', '>=', 21)
    # Returns: 'age < 21'
    
    # Equality negation returns OR expression
    result = negate_comparison('age', '==', 21)
    # Returns: (('age', '<', 21), ('age', '>', 21))

Exception Classes
-----------------

.. autoexception:: NumericAttributeError
.. autoexception:: BitOverflowError
.. autoexception:: InvalidBitWidthError
.. autoexception:: InvalidOperatorError
.. autoexception:: AttributeNameConflictError

Low-Level Functions
-------------------

These functions are used internally but can be called directly for advanced use cases.

.. autofunction:: int_to_bits
.. autofunction:: expand_numeric_comparison
.. autofunction:: preprocess_numeric_policy

