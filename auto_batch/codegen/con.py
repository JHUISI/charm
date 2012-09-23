addTypeAST = 'Add'
ASTParser = 'ASTParser'
ASTVarVisitor = 'ASTVarVisitor'
backSlash = '\\'
batchInputsString = 'batch inputs'
batchVerifierOutputAssignment = ' := '
binOpTypeAST = 'BinOp'
binOpValue = 'BinOpValue'
booleanType = 'bool'
callValue = 'CallValue'
callTypeAST = 'Call'

codeGenHeader = "<====	PREP FOR CODE GEN	====>"

codeString = 'Code '

commentChar = '#'
computeString = 'Compute:  '

cppTemplate = 'cppTemplate.cpp'

delta = 'delta'
deltaDictName = 'delta'
deltaPrecomputeVarString = 'delta := '
dictBeginChar = '['
dictTypeAST = 'Dict'
dictTypePython = 'dict'
dictValue = 'DictValue'
divTypeAST = 'Div'
dotDirector = 'on'
dotOperation = 'dot'
dotPrefix = 'dot'
dotProdType = 'dotprod'
dotProdValue = 'DotProdValue'
doubleQuote = "\""

eqChecksIndex = 't'
numEqChecks = 'n'

equals = 'Eq()'
expTypeAST = 'Pow'
finalBatchEqString = 'Final batch eq: '
finalBatchEqWithLoopsString = 'Final version => '
forLoopTypeAST = 'For'
floatValue = 'FloatValue'
floatTypePython = 'float'
functionArgMap = 'FunctionArgMap'
funcNamesNotToTest = ['visit_FunctionDef']
G1 = 'G1'
G2 = 'G2'
GT = 'GT'
ZR = 'ZR'
group = 'group'
groupTypes = [G1, G2, GT, ZR]
hashType = 'hash'
hashTypesCharm = ['hash', 'H', 'H2']
hashValue = 'HashValue'
idType = 'id'
indexTypeAST = 'Index'
initFuncName = 'init'
initType = 'init'
initValue = 'InitValue'
integerValue = 'IntegerValue'
intTypePython = 'int'

invertTypeAST = 'Invert'

lambdaArgBegin = 'LAMBDA_ARG_BEGIN'
lambdaArgEnd = 'LAMBDA_ARG_END'
lambdaTypeAST = 'Lambda'
lambdaTypeCharm = 'lambda'
lambdaValue = 'LambdaValue'
left = 'left'


lineNoType = 'lineno'
lineNumbers = 'LineNumbers'

linesNotToWrite = ['PKSig.__init__ ( self )']

listInString = ' in '
listString = 'List := '

listTypeAST = 'List'

listTypePython = 'list'

listValue = 'ListValue'

loopBlock = 'LoopBlock'
loopIndicator = '_'
loopIndicesSeparator = '%'
loopInfo = 'LoopInfo'
lParan = '('
mainFuncName = 'main'
mathOp = ('left', 'op', 'right')
maxStrLengthForLoopNames = 4
messageType = 'M_Type'
multTypeAST = 'Mult'
nameOnlyTypeAST = 'Name'
nameString = 'name'
newLineChar = '\n'
numSignatures = 'N'
numSignaturesIndex = 'z'
numSigners = 'l'
numSignersIndex = 'y'
numTypeAST = 'Num'
operationValue = 'OperationValue'
pair = 'pair'
pairingLetter = 'e'
precomputeString = 'Precompute: '
precomputeVarString = 'pre'
productString = 'prod'
pySuffix = '.py'
pythonLoopPrefixes = ['for ', 'while ']

randomType = 'random'
randomValue = 'RandomValue'
range = 'range'
returnTypeAST = 'Return'
right = 'right'
self = 'self'
selfFuncArgString = ' self , '
selfFuncCallString = ' self.'
singleQuote = "'"
sliceValue = 'SliceValue'
sliceType_LowerUpperStep = 'SliceType_LowerUpperStep'
sliceType_Value = 'SliceType_Value'
sliceTypes = [sliceType_LowerUpperStep, sliceType_Value]

sortString = 'Sort := '

space = ' '
stringName = 'StringName'
stringValue = 'StringValue'
strOnlyTypeAST = 'Str'
strTypeAST = ['Name', 'Str']
strTypePython = 'str'
subTypeAST = 'Sub'
subscriptFields = ('value', 'slice', 'ctx')
subscriptIndicator = '#'

subscriptTerminator = '?'

subscriptTypeAST = 'Subscript'
subscriptName = 'SubscriptName'
sumDirector = 'of'
sumOperation = 'sum'
sumPrefix = 'sum'
sumString = 'sum'
tupleTypeAST = 'Tuple'

tupleValue = 'TupleValue'

typeString = 'Type: '

unaryOpTypeAST = 'UnaryOp'
unaryOpValue = 'UnaryOpValue'
uSubTypeAST = 'USub'
valueType = 'value'
variable = 'Variable'
variableDependencies = 'VariableDependencies'
variableNamesValue = 'VariableNamesValue'
variablesString = 'variables'
verifyFuncName = 'verify'
batchEqRemoveStrings = [pairingLetter, lParan, numSignersIndex, numSignaturesIndex, '1', productString, '{', '}', numSigners, numSignatures, ':=', '^', ',', dotDirector, ')', '==', '*', sumDirector, sumString]
opTypesAST = [addTypeAST, divTypeAST, expTypeAST, multTypeAST, subTypeAST]
loopPrefixes = [dotPrefix, sumPrefix]
loopTypes = [numSignatures, numSigners, numEqChecks]
loopIndexTypes = [numSignaturesIndex, numSignersIndex, eqChecksIndex]
operationTypes = [dotOperation, sumOperation]
quoteCharTypes = [singleQuote, doubleQuote]
reservedWords = ['len', 'random', 'print', pair, 'class', 'pickleObject', 'elif', 'True', 'False', '__init__', 'global', 'str', 'int', 'float', 'return', 'def', dotPrefix, productString, group, G1, G2, GT, dotProdType, range, 'lam_func', ZR, self, 'for', 'in', 'while', 'if', 'pass', sumString, 'e']
reservedSymbols = ['..', lParan, ')', '{', '}', ':=', '=', '-', '*', '^', '/', ',', '==', ':', '[', ']', '**', '+']
unaryOpTypesAST = [invertTypeAST, uSubTypeAST]
variableNameTypes = [stringName, subscriptName]

eqChecksSuffix = subscriptIndicator + eqChecksIndex
leftAndRightTypesMustMatch = [addTypeAST, divTypeAST, multTypeAST, subTypeAST]
