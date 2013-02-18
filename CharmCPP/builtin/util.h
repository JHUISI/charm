/*!	\file util.h
 *
 *	\brief Routines that are shared among the schemes in the Functional Encryption Library.
 *  
 *	Copyright 2012 Matthew Green. All rights reserved.
 */

#ifndef __UTIL_H__
#define __UTIL_H__

/**
 * Constants
 */

#define TRUE	1
#define FALSE	0
#define SAFE_MALLOC(size)	malloc(size)
#define SAFE_FREE(val)		free(val)
//#define LOG_ERROR(...)		if (global_error_file != NULL) ( fprintf (global_error_file, __VA_ARGS__), fprintf(global_error_file, " (%s:%d)\n" , __FILE__, __LINE__))

/*
 * Data Structures
 */

typedef unsigned int uint32;
typedef unsigned short uint16;
typedef int	int32;
typedef short int16;
typedef unsigned char uint8;
typedef char int8;
typedef int Bool;
typedef int element_t; // tmp decl (how to make this truly abstract?)
typedef int pairing_t; // tmp decl (how to make this truly abstract?)

typedef enum _CHARM_ERROR {
	CHARM_ERROR_NONE = 0,
	CHARM_ERROR_INVALID_CONTEXT,
	CHARM_ERROR_INVALID_CIPHERTEXT,
	CHARM_ERROR_INVALID_GROUP_PARAMS,
	CHARM_ERROR_INVALID_GLOBAL_PARAMS,
	CHARM_ERROR_INVALID_KEY,
	CHARM_ERROR_OUT_OF_MEMORY,
	CHARM_ERROR_INVALID_INPUT,
	CHARM_ERROR_INVALID_PLAINTEXT,
	CHARM_ERROR_UNKNOWN_SCHEME,
	CHARM_ERROR_LIBRARY_NOT_INITIALIZED,
	CHARM_ERROR_NOT_IMPLEMENTED,
	CHARM_ERROR_NO_SECRET_PARAMS,
	CHARM_ERROR_NO_PUBLIC_PARAMS,
	CHARM_ERROR_BUFFER_TOO_SMALL,
	CHARM_ERROR_UNKNOWN
} CHARM_ERROR;

typedef enum _CHARM_INPUT_TYPE {
	CHARM_INPUT_NONE = 0,
	CHARM_INPUT_ATTRIBUTE_LIST,
	CHARM_INPUT_NM_ATTRIBUTE_POLICY
} CHARM_INPUT_TYPE;

typedef enum _CHARM_ATTRIBUTE_NODE_TYPE {
	CHARM_ATTRIBUTE_POLICY_NODE_NULL = 0,
	CHARM_ATTRIBUTE_POLICY_NODE_LEAF,
	CHARM_ATTRIBUTE_POLICY_NODE_AND,
	CHARM_ATTRIBUTE_POLICY_NODE_OR,
	CHARM_ATTRIBUTE_POLICY_NODE_THRESHOLD
} CHARM_ATTRIBUTE_NODE_TYPE;

/* Number of ciphertext attributes (maximum)	*/
#define	MAX_CIPHERTEXT_ATTRIBUTES	1000

/* Maximum attribute string length in bytes (this includes a NULL termination byte.) */
#define MAX_ATTRIBUTE_STR	256

/* Maximum serialized policy string in bytes (this includes a NULL termination byte.) */
#define	MAX_POLICY_STR		2048

#define BITS 32

/**
 *  Attribute structure.  Contains a null-terminated string (or NULL) and/or a hashed attribute
 *	typically an element of Zr.  The attribute_hash member should only be accessed if the
 *	is_hashed flag is TRUE.
 */

typedef struct _charm_attribute {
	uint8			attribute_str[MAX_ATTRIBUTE_STR];	/* Attribute as string.	*/
	element_t		attribute_hash;						/* Optional: attribute hashed to an element.	*/
	Bool			is_hashed;
	Bool			is_negated;
	element_t		share;								/* Optional: secret share value.	*/
	Bool			contains_share;
} charm_attribute;

typedef struct _charm_function_input {
	CHARM_INPUT_TYPE		input_type;
	void*					scheme_input;
} charm_function_input;

/**
 *  Attribute list data structure.
 */

typedef struct _charm_attribute_list {
	uint32					num_attributes;
	struct _charm_attribute	*attribute;		/* Array of charm_attribute structures.	*/
} charm_attribute_list;

/**
 *  Attribute subtree data structure.
 */

typedef struct _charm_attribute_subtree {
	CHARM_ATTRIBUTE_NODE_TYPE		node_type;
	charm_attribute					attribute;
	Bool							is_negated;
	uint32							num_subnodes;
	uint32							threshold_k;
	Bool							use_subnode;
	struct _charm_attribute_subtree	**subnode;
} charm_attribute_subtree;

/*!
 *  Attribute policy data structure.
 */

typedef struct _charm_attribute_policy {
	charm_attribute_subtree		*root;
	char 						*str;
} charm_attribute_policy;

/* Prototypes			*/

/*!
 * Parse a function input as an attribute list.  This will involve some memory allocation in the
 * charm_attribute_list structure, which must be cleared using the charm_attribute_list_clear call.
 *
 * @param input				Attribute list
 * @param num_attributes	Number of attributes is written here
 * @param attribute_list	charm_attribute_list structure
 * @return					CHARM_ERROR_NONE or an error code.
 */

CHARM_ERROR	charm_parse_input_as_attribute_list(charm_function_input *input, charm_attribute_list *attribute_list,
									  pairing_t pairing);

/*!
 * Parse a function input as an attribute policy.  This will involve some memory allocation in the
 * charm_attribute_poliy structure, which must be cleared using the charm_attribute_policy_clear call.
 *
 * @param input				Attribute list
 * @param num_attributes	Number of attributes is written here
 * @param attribute_list	charm_attribute_list structure
 * @return					CHARM_ERROR_NONE or an error code.
 */

CHARM_ERROR	charm_parse_input_as_attribute_policy(charm_function_input *input, charm_attribute_policy *policy);

/*!
 * Convert an array of attribute strings into a charm_function_input.  The input
 * structure must be initialized, although some additional memory allocation will
 * occur.
 *
 * @param input				Pointer to an allocated charm_function_input structure
 * @param attribute_list	Array of char* strings containing attributes
 * @param num_attributes	Number of attributes in list
 * @return					CHARM_ERROR_NONE or an error code.
 */

//CHARM_ERROR	charm_create_attribute_list_from_strings(charm_function_input *input, char **attributes, uint32 num_attributes);
CHARM_ERROR charm_create_attribute_list_from_strings(charm_attribute_list *attribute_list, char **attributes, uint32 num_attributes);

/*!
 * This recursive function counts the number of leaves under a given subtree.
 *
 * @param charm_attribute_subtree	Pointer to a charm_attribute_subtree structure.
 * @param attribute_list			Pointer to a charm_attribute_list structure.
 * @return							Total number of satisfied leaves
 */

uint32	charm_count_policy_leaves(charm_attribute_subtree *subtree);
CHARM_ERROR charm_get_policy_leaves(charm_attribute_subtree *subtree, charm_attribute_list *attribute_list, uint32 *index);

/*!
 * Allocate memory for an attribute list of num_attributes attributes.
 *
 * @param attribute_list	charm_attribute_list structure
 * @return					CHARM_ERROR_NONE or an error code.
 */

CHARM_ERROR	charm_attribute_list_initialize(charm_attribute_list *attribute_list, uint32 num_attributes);

/*!
 * Find the index of an attribute within the list.  This searches on either the
 * attribute_hash or the attribute_str value (in that order) depending
 * on which is available.  
 *
 * @param attribute			Pointer to a charm_attribute structure
 * @param attribute_list	Pointer to a charm_attribute_list structure
 * @return					The index or -1 if not found.
 */

int32	charm_get_attribute_index_in_list(charm_attribute *attribute, charm_attribute_list *attribute_list);

/*!
 * Convert an array of attribute strings into a charm_function_input.  The input
 * structure must be NULL, although some additional memory allocation will
 * occur.
 *
 * @param attribute_list	Pointer to an unallocated charm_attribute_list structure
 * @return					CHARM_ERROR_NONE or an error code.
 */

charm_attribute_list *charm_create_func_input_for_attributes(char *attributes);

/*!
 * Convert an policy string into a charm_function_input.  The input
 * structure must be initialized, although some additional memory allocation will
 * occur.
 *
 * @param input				Pointer to an allocated charm_function_input structure
 * @param policy			char* strings containing policy using attributes
 * @return					CHARM_ERROR_NONE or an error code.
 */

charm_attribute_policy *charm_create_func_input_for_policy(char *policy);

/*!
 * Clear an charm_function_input structure for attributes or policy and deallocates memory.
 *
 * @param input				functional input structure
 * @return					CHARM_ERROR_NONE or an error code.
 */

CHARM_ERROR	charm_func_input_clear(charm_function_input *input);

/*!
 * Clear an attribute list data structure, deallocating memory.
 *
 * @param attribute_list	charm_attribute_list structure
 * @return					CHARM_ERROR_NONE or an error code.
 */

CHARM_ERROR	charm_attribute_list_clear(charm_attribute_list *attribute_list);
CHARM_ERROR charm_attribute_list_free(charm_attribute_list *attribute_list);

/*!
 * Duplicate an attribute list data structure.  Assumes that the incoming attribute
 * list structure is /not/ previously allocated.  This function allocates the new
 * attribute list: the user must call charm_attribute_list_clear() when done with it.
 *
 * @param attribute_list_DST	charm_attribute_list structure destination.
 * @param attribute_list_SRC	charm_attribute_list structure source.
 * @param group_params			charm_group_params structure.
 * @return						CHARM_ERROR_NONE or an error code.
 */

CHARM_ERROR	charm_attribute_list_copy(charm_attribute_list *attribute_list_DST, charm_attribute_list *attribute_list_SRC, pairing_t pairing);

/*!
 * Serialize an attribute list structure.  If "buffer" is NULL this returns the necessary length
 * only.
 *
 * @param attribute_list		charm_attribute_list pointer.
 * @param buffer				Buffer or "NULL" to get length.
 * @param buf_len				Size of the buffer in bytes.
 * @param result_len			Result length.
 * @return						CHARM_ERROR_NONE or an error code.
 */

CHARM_ERROR	charm_attribute_list_to_buffer(charm_attribute_list *attribute_list, uint8 *buffer, size_t buf_len, size_t *result_len);

/*!
 * Parse a string of attributes into an charm_attribute_list structure.
 * 
 * @param str_list				Buffer to attribute list string.
 * @param attribute_list		charm_attribute_list pointer.
 */
CHARM_ERROR  charm_buffer_to_attribute_list(char **str_list, charm_attribute_list *attribute_list);

/*!
 * Clear an attribute data structure, deallocating memory.
 *
 * @param subtree		charm_attribute_subtree structure
 * @return				CHARM_ERROR_NONE or an error code.
 */

CHARM_ERROR	charm_attribute_clear(charm_attribute *attribute);

/*!
 * Clear an attribute subtree data structure, deallocating internal memory.
 *
 * @param subtree		charm_attribute_subtree structure
 * @return				CHARM_ERROR_NONE or an error code.
 */

CHARM_ERROR	charm_attribute_subtree_clear(charm_attribute_subtree *subtree);

/*!
 * Duplicate an attribute.  The destination structure should be uninitialized.
 *
 * @param attribute_DST			charm_attribute structure destination.
 * @param attribute_SRC			charm_attribute structure source.
 * @return						CHARM_ERROR_NONE or an error code.
 */

CHARM_ERROR	charm_attribute_copy(charm_attribute *attribute_DST, charm_attribute *attribute_SRC, pairing_t pairing);

/*!
 * Recursively print a policy tree into an ASCII string.
 *
 * @param charm_attribute_subtree	Pointer to a charm_attribute_subtree structure.
 * @param output_str				Pointer to a character string.
 * @param str_len					Maximum length of the buffer
 * @return							CHARM_ERROR_NONE or an error code.
 */

CHARM_ERROR	charm_attribute_policy_to_string(charm_attribute_subtree *subtree, char *output_str, size_t buf_len);

/***************************************************************************
 * Policy manipulation
 ***************************************************************************/

/*!
 * Create a policy leaf subnode from an attribute string.
 *
 * @param attribute_str			Attribute string.
 * @return						Allocated policy subnode.
 */

charm_attribute_subtree*	charm_policy_create_leaf(char *attribute_str);

/*!
 * Create a policy subnode from an array of subnodes.
 *
 * @param node_type			CHARM_ATTRIBUTE_NODE_TYPE value.
 * @param num_subnodes		Number of subnodes in the array.
 * @param threshold_k		Threshold value k.
 * @param subnodes			Array of charm_attribute_subtree pointers.
 * @return					Allocated policy subnode.
 */

charm_attribute_subtree*	charm_policy_create_node(CHARM_ATTRIBUTE_NODE_TYPE node_type, uint32 num_subnodes, uint32 threshold_k, charm_attribute_subtree **subnodes);

/*!
 * Recursively compact a tree structure.  This consists of combining parent
 * and child nodes where appropriate. 
 *
 * The process is nicked from John Bethencourt's library, though the code isn't.
 *
 * @param subtree			The subtree.
 */

void	charm_policy_compact(charm_attribute_subtree* subtree);

/*!
 * Merge a child into the subtree.  Only works if the parent and child
 * node are both OR nodes or both AND nodes.
 *
 * @param subtree			The subtree.
 * @param child_num			Index of the child.
 */

void	charm_policy_merge_child(charm_attribute_subtree* subtree, uint32 child_num);

/*!
 * Extend an array of charm_attribute_subtree pointers.
 *
 * @param attributes		The original array.
 * @param old_nodes			Number of nodes in the original array.
 * @param new_nodes			Desired number of nodes.
 */

charm_attribute_subtree **charm_policy_extend_array(charm_attribute_subtree **attributes, uint32 old_nodes, uint32 new_nodes);

/*!
 * Parse a string to obtain an attribute policy.
 *
 * @param policy		A charm_attribute_policy structure.
 * @param policy_str	The policy string.
 * @param CHARM_ERROR_NONE or an error code
 */

CHARM_ERROR	charm_policy_from_string(charm_attribute_policy *policy, char *policy_str);

/*!
 * Parse attribute policy to obtain the string.
 *
 * @param policy		A charm_attribute_policy structure.
 * @param string or NULL if policy structure is empty.
 */

char* charm_get_policy_string(charm_attribute_policy *policy);

int num_bits(int value);

/*!
 * This recursive function counts the total number of leaves in a policy.
 *
 * @param charm_attribute_subtree	Pointer to a charm_attribute_subtree structure.
 * @return							Total number of leaves.
 */

uint32 prune_tree(charm_attribute_subtree *subtree, charm_attribute_list *attribute_list);

CHARM_ERROR charm_get_pruned_attributes(charm_attribute_subtree *subtree, charm_attribute_list *attribute_list, uint32 *index);

void debug_print_policy(charm_attribute_policy *policy_tree);

void debug_print_attribute_list(charm_attribute_list *attribute_list);

#endif /* ifdef __UTIL_H__ */
