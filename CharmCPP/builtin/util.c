/*!	\file util.c
 *
 *	\brief Routines supporting Attribute Based Encryption.
 *  
 *	Copyright 2012 Matthew Green. All rights reserved.
 */

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include "util.h"
#include "policy.h"

/*!
 * Parse a function input as an attribute list.  This will involve some memory allocation in the
 * charm_attribute_list structure, which must be cleared using the charm_attribute_list_clear call.
 *
 * @param input				Attribute list
 * @param num_attributes	Number of attributes is written here
 * @param attribute_list	charm_attribute_list structure
 * @return					CHARM_ERROR_NONE or an error code.
 */

CHARM_ERROR charm_parse_input_as_attribute_list(charm_function_input *input, charm_attribute_list *attribute_list, pairing_t pairing)
{
	CHARM_ERROR result;
	
	if (attribute_list == NULL) {
		return CHARM_ERROR_INVALID_INPUT;
	}
	
	/* Wipe the attribute list structure clean.	*/
	memset(attribute_list, 0, sizeof(charm_attribute_list));
	
	/* Can't parse invalid inputs.	*/
	if (input->input_type != CHARM_INPUT_ATTRIBUTE_LIST) {
		return CHARM_ERROR_INVALID_INPUT;
	}
	
	if (attribute_list == NULL || input->scheme_input == NULL) {
		//LOG_ERROR("charm_parse_input_as_attribute_list: could not parse function input as an attribute list");
		return CHARM_ERROR_INVALID_INPUT;
	}
	
	/* Clear the attribute list data structure and copy the scheme input.	*/
	memset(attribute_list, 0, sizeof(charm_attribute_list));
	result = charm_attribute_list_copy(attribute_list, (charm_attribute_list*)input->scheme_input, pairing);
	
	return CHARM_ERROR_NONE;
}

/*!
 * Parse a function input as an attribute policy.  This will involve some memory allocation in the
 * charm_attribute_poliy structure, which must be cleared using the charm_attribute_policy_clear call.
 *
 * @param input				Attribute list
 * @param num_attributes	Number of attributes is written here
 * @param attribute_list	charm_attribute_list structure
 * @return					CHARM_ERROR_NONE or an error code.
 */

CHARM_ERROR
charm_parse_input_as_attribute_policy(charm_function_input *input, charm_attribute_policy *policy)
{
	if (policy == NULL) {
		return CHARM_ERROR_UNKNOWN;
	}
	
	if (input->input_type != CHARM_INPUT_NM_ATTRIBUTE_POLICY) {
		return CHARM_ERROR_INVALID_INPUT;
	}
	
	/* Clear the attribute list data structure.	*/
	// TODO: Do we still need a copy here?
	// LOG_ERROR("charm_parse_input_as_attribute_policy: need to add a copy");
	memcpy(policy, (charm_attribute_policy*)(input->scheme_input), sizeof(charm_attribute_policy));
		
	return CHARM_ERROR_NONE;
}

/*!
 * Convert an array of attribute strings into a charm_function_input.  The input
 * structure must be initialized, although some additional memory allocation will
 * occur.
 *
 * @param input				Pointer to an allocated charm_function_input structure
 * @param attribute_list	Array of char* strings containing attributes (set to NULL)
 * @return					CHARM_ERROR_NONE or an error code.
 */

charm_attribute_list *charm_create_func_input_for_attributes(char *attributes)
{
	CHARM_ERROR err_code = CHARM_ERROR_NONE;
	
	/* Allocate an attribute list data structure.	*/
	charm_attribute_list *attribute_list = (charm_attribute_list*)SAFE_MALLOC(sizeof(charm_attribute_list));
	if (attribute_list == NULL) {
		//LOG_ERROR("%s: could not allocate attribute list", __func__);
		return NULL;
	}
	
	/* Construct attribute list from string */
	err_code = charm_buffer_to_attribute_list(&attributes, attribute_list);
	if(err_code != CHARM_ERROR_NONE) {
		free(attribute_list);
		//LOG_ERROR("%s: invalid attribute string", __func__);
		return NULL;
	}

	return attribute_list;
}

/*!
 * Convert an policy string into a charm_function_input.  The input
 * structure must be initialized, although some additional memory allocation will
 * occur.
 *
 * @param input				Pointer to an allocated charm_function_input structure
 * @param policy			char* strings containing policy using attributes
 * @return					CHARM_ERROR_NONE or an error code.
 */

charm_attribute_policy *charm_create_func_input_for_policy(char *policy)
{
	CHARM_ERROR err_code;
	charm_attribute_policy *charm_policy = NULL;
	
	/* Allocate an charm_attribute_policy data structure */
	charm_policy = (charm_attribute_policy *) SAFE_MALLOC(sizeof(charm_attribute_policy));
	if(charm_policy == NULL) {
		//LOG_ERROR("%s: could not allocate charm policy", __func__);
		return NULL;
	}
	memset(charm_policy, 0, sizeof(charm_attribute_policy));
	
	/* Construct/parse policy string into a structure */
	err_code = charm_policy_from_string(charm_policy, policy);
	if(err_code != CHARM_ERROR_NONE) {
		free(charm_policy);
		//LOG_ERROR("%s: invalid charm policy string", __func__);
		return NULL;
	}
	
	return charm_policy;
}

/*!
 * Convert an array of attribute strings into a charm_function_input.  The input
 * structure must be initialized, although some additional memory allocation will
 * occur.
 *
 * @param input				Pointer to an allocated charm_function_input structure
 * @param attribute_list	Array of char* strings containing attributes
 * @param num_attributes	Number of attributes in list
 * @return					CHARM_ERROR_NONE or an error code.
 * @DEPRECATED
 */
CHARM_ERROR charm_create_attribute_list_from_strings(charm_attribute_list *attribute_list, char **attributes, uint32 num_attributes)
{
	CHARM_ERROR err_code;
	uint32 i;
	
	/* Allocate an attribute list data structure.	*/
	attribute_list = (charm_attribute_list*)SAFE_MALLOC(sizeof(charm_attribute_list));
	if (attribute_list == NULL) {
		//LOG_ERROR("charm_create_attribute_list_from_strings: could not allocate attribute list");
		return CHARM_ERROR_OUT_OF_MEMORY;
	}
	
	/* Initialize the structure.	*/
	memset(attribute_list, 0, sizeof(charm_attribute_list));
	err_code = charm_attribute_list_initialize(attribute_list, num_attributes);
	if (err_code != CHARM_ERROR_NONE) {
		//LOG_ERROR("charm_create_attribute_list_from_strings: could not initialize attribute list");
		return err_code;
	}

	/* Copy the strings into the attribute list.	*/
	for (i = 0; i < num_attributes; i++) {
		strcpy((char *) attribute_list->attribute[i].attribute_str, (const char *) attributes[i]);
	}
	
//	input->scheme_input = (void*)attribute_list;
//	input->input_type = CHARM_INPUT_ATTRIBUTE_LIST;
	
	return CHARM_ERROR_NONE;
}

/*!
 * Allocate the internals of an attribute list of num_attributes attributes.
 *
 * @param attribute_list	charm_attribute_list structure
 * @return					CHARM_ERROR_NONE or an error code.
 */

CHARM_ERROR charm_attribute_list_initialize(charm_attribute_list *attribute_list, uint32 num_attributes)
{
	uint32 i;
	
	/* Sanity check.	*/
	if (num_attributes < 1 || num_attributes > MAX_CIPHERTEXT_ATTRIBUTES) {
		return CHARM_ERROR_INVALID_INPUT;
	}
	
	/* Initialize the structure and allocate memory for the attribute structures.	*/
	memset(attribute_list, 0, sizeof(charm_attribute_list));
	attribute_list->num_attributes = num_attributes;
	attribute_list->attribute = SAFE_MALLOC(sizeof(charm_attribute) * num_attributes);
	if (attribute_list->attribute == NULL) {
		return CHARM_ERROR_OUT_OF_MEMORY;
	}
	
	/* Wipe the attribute structures clean.	*/
	for (i = 0; i < num_attributes; i++) {
		attribute_list->attribute[i].is_hashed = FALSE;
		attribute_list->attribute[i].attribute_str[0] = 0;
		attribute_list->attribute[i].is_negated = FALSE;	// must check string for '!' to set this to TRUE
	}

	return CHARM_ERROR_NONE;
}

/*!
 * Clear an charm_function_input structure for attributes or policy and deallocates memory.
 *
 * @param input				functional input structure
 * @return					CHARM_ERROR_NONE or an error code.
 */

CHARM_ERROR
charm_func_input_clear(charm_function_input *input)
{	
	if(input->input_type == CHARM_INPUT_ATTRIBUTE_LIST) {
		charm_attribute_list *attribute_list = (charm_attribute_list *) input->scheme_input;
		charm_attribute_list_clear(attribute_list);
	}
	else if(input->input_type == CHARM_INPUT_NM_ATTRIBUTE_POLICY) {
		charm_attribute_policy *attribute_policy = (charm_attribute_policy *) input->scheme_input;
		free(attribute_policy->str);
		free(attribute_policy->root);
		free(attribute_policy);
	}
	
	return CHARM_ERROR_NONE;
}

/*!
 * Clear an attribute list data structure, deallocating memory.
 *
 * @param attribute_list	charm_attribute_list structure
 * @return					CHARM_ERROR_NONE or an error code.
 */

CHARM_ERROR
charm_attribute_list_clear(charm_attribute_list *attribute_list)
{
	int i;
	
	/* Clear out the attributes in the list.	*/
	for (i = 0; (unsigned) i < attribute_list->num_attributes; i++) {
		charm_attribute_clear(&(attribute_list->attribute[i]));
	}

	memset(attribute_list, 0, sizeof(charm_attribute_list));
	
	return CHARM_ERROR_NONE;
}

CHARM_ERROR
charm_attribute_list_free(charm_attribute_list *attribute_list)
{
	uint32 i;

	/* Clear out the attributes in the list.	*/
	for (i = 0; i < attribute_list->num_attributes; i++) {
		charm_attribute_clear(&(attribute_list->attribute[i]));
	}

	SAFE_FREE(attribute_list->attribute);
	memset(attribute_list, 0, sizeof(charm_attribute_list));
	SAFE_FREE(attribute_list);
	return CHARM_ERROR_NONE;
}

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

CHARM_ERROR
charm_attribute_list_copy(charm_attribute_list *attribute_list_DST, charm_attribute_list *attribute_list_SRC, pairing_t pairing)
{
	CHARM_ERROR err_code;
	int i;
	
	err_code = charm_attribute_list_initialize(attribute_list_DST, attribute_list_SRC->num_attributes);
	if (err_code != CHARM_ERROR_NONE) {
		return err_code;
	}

	/* Duplicate the contents of each charm_attribute structure.	*/
	for (i = 0; (unsigned) i < attribute_list_SRC->num_attributes; i++) {
		/* Copy attribute #i	*/		
		err_code = charm_attribute_copy((charm_attribute*)&(attribute_list_DST->attribute[i]), (charm_attribute*)&(attribute_list_SRC->attribute[i]), pairing);
		if (err_code != CHARM_ERROR_NONE) {
			charm_attribute_list_clear(attribute_list_DST);
			return err_code;
		}
	}
	
	return CHARM_ERROR_NONE;
}

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

CHARM_ERROR
charm_attribute_list_to_buffer(charm_attribute_list *attribute_list, uint8 *buffer, size_t buf_len, size_t *result_len)
{
	// TODO: JAA cleanup.
	uint32 i;
	uint8 *buf_ptr = buffer;
	//char token[300];
	
	*result_len = 0;	
	
	if (attribute_list == NULL) {
		return CHARM_ERROR_INVALID_INPUT;
	}
	
	/* Begin with a paren.	*/
	(*result_len)++;
	if (buffer != NULL) {	buf_ptr += snprintf((char*)buf_ptr, (buf_len - *result_len), "("); 	}
	
	/* Serialize all of the elements.	*/
	for (i = 0; i < attribute_list->num_attributes; i++) {
		// printf("%i:%s\n", i, attribute_list->attribute[i].attribute_str);
		/* We prefer the attribute string.	*/
			if (i != 0) {
				if (buffer != NULL) {	
					/* MDG: 7/4/2010 commented out what look like unnecessary arguments. i.e. ');'	*/
					buf_ptr += snprintf((char*) buf_ptr, (buf_len - *result_len), ",", attribute_list->attribute[i].attribute_str);
				}
				(*result_len)++;
			}

		if (attribute_list->attribute[i].attribute_str[0] != 0)	{
			if (buffer != NULL) {	buf_ptr += snprintf((char *) buf_ptr, (buf_len - *result_len), "%s", attribute_list->attribute[i].attribute_str);	}
			
			/* JAA removed quotes around attributes to make parsing straightforward */
			*result_len += strlen((char *) attribute_list->attribute[i].attribute_str);  // + 2;
		} else if (attribute_list->attribute[i].is_hashed == TRUE) {
			// element_snprintf(token, 300, "{%B}", attribute_list->attribute[i].attribute_hash);
			// if (buffer != NULL) {	buf_ptr += snprintf((char *) buf_ptr, (buf_len - *result_len), "%s", token);	}
			//*result_len += strlen(token) + 2;
		} else {
			return CHARM_ERROR_INVALID_INPUT;
		}
	}
	
	/* End with another paren.	*/
	(*result_len)++;
	if (buffer != NULL) {	buf_ptr += snprintf((char *) buf_ptr, (buf_len - *result_len), ")");	}
	
	return CHARM_ERROR_NONE;
}


/*!
 * Parse a string of attributes into an charm_attribute_list structure.
 * 
 * @param str_list				Buffer to attribute list string.
 * @param attribute_list		charm_attribute_list pointer (not pre-allocated).
 * @return						CHARM_ERROR_NONE or an error code.
 */
CHARM_ERROR
charm_buffer_to_attribute_list(char **str_list, charm_attribute_list *attribute_list)
{
	// form "( 'ATTR1' , 'ATTRX' )" => token '(' ','
	CHARM_ERROR err_code = CHARM_ERROR_NONE;
	int i = 0, j, token_len;
	uint32 num_attributes = 0;
	char delims[] = "(,)", tmp[BITS+1];
	char *list_cpy = strdup(*str_list);
	char *token = strtok(list_cpy, delims);
	char *s;	
	memset(tmp, 0, BITS+1);
	
	/* count the number of attributes in the list */
	do {
		/* check for '=' => numerical attributes */
		if((s = strchr(token, '=')) != NULL) {
			char *value = malloc(strlen(s+1));
			strncpy(value, s+1, strlen(s+1));
			int num = atoi(value);
			if(num > 0) {
				num_attributes += num_bits(num) + 1;		
			}
			else {
				//LOG_ERROR("%s: cannot have negative non-numerical attributes",value);
				free(value);
				return CHARM_ERROR_INVALID_INPUT;
			}
			// num_attributes++;
			free(value);
		}
		else {
			num_attributes++;
		}
		token = strtok(NULL, delims);
	} while(token != NULL);
		
	/* Initialize the structure.	*/
	if(attribute_list == NULL) {
		/* malloc in case the pointer is NULL */
		attribute_list = (charm_attribute_list *) malloc(sizeof(charm_attribute_list));
	}
	memset(attribute_list, 0, sizeof(charm_attribute_list));
	err_code = charm_attribute_list_initialize(attribute_list, num_attributes);
	if (err_code != CHARM_ERROR_NONE) {
		//LOG_ERROR("%s: could not initialize attribute list", __func__);
		return err_code;
	}	
	
	/* tokenize and store in charm_attribute_list */
	token = strtok(*str_list, delims);
	// printf("%s: %i = token = '%s'?\n", __func__, i, token);
	while (token != NULL && i <= MAX_CIPHERTEXT_ATTRIBUTES) {
		token_len = strlen(token);

		/* check for '=' => numerical attributes */
		if((s = strchr(token, '=')) != NULL) {
			char *attr = malloc(s - token);
			char *value = malloc(strlen(s+1));
			strncpy(attr, token, (s - token));
			strncpy(value, s+1, strlen(s+1));
			int val = atoi(value);			
			int num = num_bits(val);
			int str_len = token_len + 13;
			
			if(str_len < MAX_ATTRIBUTE_STR) {
				memset(attribute_list->attribute[i].attribute_str, 0, MAX_ATTRIBUTE_STR);
				sprintf((char *)attribute_list->attribute[i].attribute_str, "%s_flexint_uint", attr);
				i++;
			}
			
			str_len = strlen(attr) + strlen(tmp) + 9;
			for(j = 0; j < num; j++) {
				memset(tmp, 'x', BITS);
				if (val & (1 << j))
		    		tmp[BITS-j-1] = '1';
				else
					tmp[BITS-j-1] = '0';
				if(str_len < MAX_ATTRIBUTE_STR) {
					memset(attribute_list->attribute[i+j].attribute_str, 0, MAX_ATTRIBUTE_STR);
					sprintf((char *)attribute_list->attribute[i+j].attribute_str, "%s_flexint_%s", attr, tmp);
				}
			}
			i += num - 1;
			free(attr);
			free(value);
		}		
		else { /* regular attributes */
			if (token_len < MAX_ATTRIBUTE_STR) {
				memset(attribute_list->attribute[i].attribute_str, 0, MAX_ATTRIBUTE_STR);
				strncpy((char *) attribute_list->attribute[i].attribute_str, token, token_len);
			}
		
			// determine if it includes a NOT '!'
			if(token[0] == '!') {
				// printf("negated token\n");
				attribute_list->attribute[i].is_negated = TRUE;
			}
		}
		
		/* retrieve next token */
		token = strtok(NULL, delims);
		i++;
	}
		
	attribute_list->num_attributes = i;

	debug_print_attribute_list(attribute_list);
	SAFE_FREE(list_cpy);
	return err_code;
}

/*!
 * Find the index of an attribute within the list.  This searches on either the
 * attribute_hash or the attribute_str value (in that order) depending
 * on which is available.  
 *
 * @param attribute			Pointer to a charm_attribute structure
 * @param attribute_list	Pointer to a charm_attribute_list structure
 * @return					The index or -1 if not found.
 */

int32
charm_get_attribute_index_in_list(charm_attribute *attribute, charm_attribute_list *attribute_list)
{
	int32 i;
	
	//if (attribute->is_hashed) { element_printf("looking for: %B\n", attribute->attribute_hash); }
	for (i = 0; i < (int32) attribute_list->num_attributes; i++) {
		/* Start by looking for matching attribute strings (if both attributes have a string.) */
		if (attribute->attribute_str[0] != 0 && attribute_list->attribute[i].attribute_str[0] != 0) {
			//printf("found: %s\n", attribute->attribute_str);
			/* If both contain a string, look for a match in the attribute string.	*/
			if (strcmp((char *) attribute->attribute_str, (char *) attribute_list->attribute[i].attribute_str) == 0) {
				/* Found a match.	*/
				return i;
			}
		}
		/* If both don't have a string, but /do/ have hashes, compare them.		*/
		else if (attribute->is_hashed == TRUE && attribute_list->attribute[i].is_hashed == TRUE) {
			//if (attribute->is_hashed) { DEBUG_ELEMENT_PRINTF("\tfound: %B\n", attribute_list->attribute[i].attribute_hash); }
			// if (element_cmp(attribute->attribute_hash, attribute_list->attribute[i].attribute_hash) == 0) {
				/* Found a match.	*/
			//	return i;
			//}
		} 
		/* If one has a hash and one has a string, compute the hash.			*/
		else if (attribute->is_hashed == TRUE && attribute_list->attribute[i].is_hashed == FALSE) {
			/* This is more of an error case.	*/
			//LOG_ERROR("PROBLEM: MATCH ISSUE");
		}
		else if (attribute->is_hashed == FALSE && attribute_list->attribute[i].is_hashed == TRUE) {
			/* This is more of an error case.	*/
			//LOG_ERROR("PROBLEM: MATCH ISSUE");
		}	
	}
	
	/* Not found.	*/
	return -1;
}

/*!
 * Clear an attribute data structure, deallocating memory.
 *
 * @param subtree		charm_attribute_subtree structure
 * @return				CHARM_ERROR_NONE or an error code.
 */

CHARM_ERROR
charm_attribute_clear(charm_attribute *attribute)
{ 
	if (attribute == NULL) {
		return CHARM_ERROR_UNKNOWN;
	}
	
	/* Clear the hashed elements of Zr (and optionally the shares), and clear out the attribute strings.	*/
	if (attribute->is_hashed == TRUE) {
		// element_clear(attribute->attribute_hash);
	}
 
	if (attribute->contains_share == TRUE) {
		// element_clear(attribute->share);
	}		
 
	memset(attribute->attribute_str, 0, sizeof(MAX_ATTRIBUTE_STR));
	
	return CHARM_ERROR_NONE;
}

/*!
 * Clear an attribute subtree data structure, deallocating memory.
 *
 * @param subtree		charm_attribute_subtree structure
 * @return				CHARM_ERROR_NONE or an error code.
 */

CHARM_ERROR charm_attribute_subtree_clear(charm_attribute_subtree *subtree)
{
	CHARM_ERROR err_code;
	uint32 i;
	
	/* Leaf nodes.							*/
	if (subtree->node_type == CHARM_ATTRIBUTE_POLICY_NODE_LEAF) {
		/* Clear the attribute.			*/
		charm_attribute_clear(&(subtree->attribute));
		return CHARM_ERROR_NONE;
	}
	
	/* Otherwise clear out the subnodes.	*/
	if (subtree->subnode != NULL) {
		/* Recurse.	 Ignore the error codes.	*/
		for (i = 0; i < subtree->num_subnodes; i++) {
			err_code = charm_attribute_subtree_clear(subtree->subnode[i]);
		}
		
		/* Deallocate the list.		*/
		SAFE_FREE(subtree->subnode);
	}
	
	return CHARM_ERROR_NONE;
}

/*!
 * Duplicate an attribute.  The destination structure should be uninitialized.
 *
 * @param attribute_DST			charm_attribute structure destination.
 * @param attribute_SRC			charm_attribute structure source.
 * @return						CHARM_ERROR_NONE or an error code.
 */

CHARM_ERROR
charm_attribute_copy(charm_attribute *attribute_DST, charm_attribute *attribute_SRC, pairing_t pairing)
{
	// CHARM_ERROR err_code;
	// element_t test;
	
	memset(attribute_DST, 0, sizeof(charm_attribute));
	
	/* Copy the contents of the structure over.	*/
	memcpy(attribute_DST->attribute_str, attribute_SRC->attribute_str, MAX_ATTRIBUTE_STR);
	attribute_DST->is_hashed = attribute_SRC->is_hashed;
	attribute_DST->is_negated = attribute_SRC->is_negated;
	
	if (attribute_SRC->is_hashed) {
		/* TODO: we're currently assuming that hashes are of Zr.  This may be a bad assumption
		 * going forward.	*/
		//element_init_Zr(test, pairing);
		//element_init_Zr(attribute_DST->attribute_hash, pairing);
		//element_set(attribute_DST->attribute_hash, attribute_SRC->attribute_hash);
	}
	
	return CHARM_ERROR_NONE;
}

/***********************************************************************************
 * Utility functions
 ***********************************************************************************/

/*!
 * Recursively print a policy tree into an ASCII string.
 *
 * @param charm_attribute_subtree	Pointer to a charm_attribute_subtree structure.
 * @param output_str				Pointer to a character string.
 * @param index						Pointer to a size_t indexing the current position in the string.
 * @param str_len					Maximum length of the string (excluding zero termination!)
 * @return							CHARM_ERROR_NONE or an error code.
 */

CHARM_ERROR
charm_attribute_policy_to_string(charm_attribute_subtree *subtree, char *output_str, size_t buf_len)
{
	CHARM_ERROR err_code;
	uint32 len = MAX_ATTRIBUTE_STR;
	char token[len], tmp[len];
	uint32 i;
	// ssize_t start = *str_index;
	//Bool use_hash = FALSE;
	memset(token, '\0', len);
	memset(tmp, '\0', len);
	/* Base case (leaf)	*/
	if (subtree->node_type == CHARM_ATTRIBUTE_POLICY_NODE_LEAF) {
		// printf("Parsing a leaf node\n");
		/* Is it negated? 
		 if (subtree->attribute.is_negated == TRUE )	{
		 if (output_str != NULL) {	snprintf((output_str+*str_index), buf_len - *str_index, "!");	}
		 (*str_index) += 1;
		 } */

		/* Use either the hash or the attribute string, whichever is shortest.	
		 if (subtree->attribute.is_hashed == TRUE) {
		 if (element_snprintf(token, 400, "{%B}", subtree->attribute.attribute_hash) == 0) {
		 LOG_ERROR("charm_attribute_policy_to_string: element is too large");
		 return CHARM_ERROR_UNKNOWN;
		 }
		 
		 if (strlen(token) < (strlen(subtree->attribute.attribute_str) + 2)) {
		 use_hash = TRUE;
		 } 
		 } */
		
	     if (strlen((char *)subtree->attribute.attribute_str) > 0) {
			//printf("FOUND ATTR: '%s'\n", subtree->attribute.attribute_str);
			if (output_str != NULL)	{	
				// snprintf((output_str+*str_index), buf_len - *str_index, "\"%s\"", subtree->attribute.attribute_str);
				sprintf(tmp, "%s", subtree->attribute.attribute_str);
				strncat(output_str, tmp, strlen(tmp));
			}
			// (*str_index) += strlen(subtree->attribute.attribute_str) + 2;
		} else {
			/* Element has neither name nor hash, can't serialize it.	*/
			return CHARM_ERROR_INVALID_INPUT;
		}
		
		return CHARM_ERROR_NONE;
	}
	
	// printf("Parsing a OPERATOR node\n");
	/* Recursive case.	*/
	switch (subtree->node_type) {
		case CHARM_ATTRIBUTE_POLICY_NODE_AND:
			sprintf(token, "and");
			break;
		case CHARM_ATTRIBUTE_POLICY_NODE_OR:
			sprintf(token, "or");
			break;
		case CHARM_ATTRIBUTE_POLICY_NODE_THRESHOLD:
			// sprintf(token, "th{%d}", subtree->threshold_k);
			sprintf(token, "%d of ", subtree->threshold_k);
			strncat(output_str, token, strlen(token));
			break;
		default:
			return CHARM_ERROR_INVALID_INPUT;
	}
	memset(tmp, '\0', len);
	/* Print the token to the output string.	*/
	if (output_str != NULL)	{	
		// snprintf((output_str+*str_index), buf_len - *str_index, "(%s ", token);	
		sprintf(tmp, "(");
		strncat(output_str, tmp, strlen(tmp));
	}
	// (*str_index) += (strlen(token) + 2);
	
	/* Recurse from left to right, spitting out the leaves.	*/
	for (i = 0; i < subtree->num_subnodes; i++) {
		if (i > 0) {			
			if (output_str != NULL && subtree->node_type == CHARM_ATTRIBUTE_POLICY_NODE_THRESHOLD) {
				strcat(output_str, ",");
			}			
			else {
				if (output_str != NULL)	{	
				// snprintf(output_str + *str_index, buf_len - *str_index, ",");	
					sprintf(tmp, " %s ", token);
					strncat(output_str, tmp, strlen(tmp));
				}
			}
			// (*str_index) += 1;
		}
		
		err_code = charm_attribute_policy_to_string(subtree->subnode[i], output_str, buf_len);
		if (err_code != CHARM_ERROR_NONE) {
			return err_code;
		}
	}
	
	if (output_str != NULL) {	
		// snprintf(output_str + *str_index, buf_len - *str_index, ")");
		strncat(output_str, ")", 1);	
	}
	// (*str_index) += 1;
	
	return CHARM_ERROR_NONE;
}

/*!
 * This recursive function counts the number of leaves
 * under a given subtree.
 *
 * @param charm_attribute_subtree	Pointer to a charm_attribute_subtree structure.
 * @param attribute_list			Pointer to a charm_attribute_list structure.
 * @return							Total number of satisfied leaves or 0 if there's a problem
 */

uint32 charm_count_policy_leaves(charm_attribute_subtree *subtree)
{
	uint32 count, i, num_leaves;
	
	if (subtree == NULL) {
		//LOG_ERROR("charm_count_policy_leaves: encountered NULL policy subtree");
		return 0;
	}			  

	/* If it's a leaf, return 1.	*/
	if (subtree->node_type == CHARM_ATTRIBUTE_POLICY_NODE_LEAF) {
		return 1;
	}
	
	/* If it's not a leaf node, there should be something under it.  Sanity check.	*/
	if (subtree->num_subnodes < 1) {
		//LOG_ERROR("charm_count_policy_leaves: encountered non-leaf subtree with no children");
		return 0;
	}
	
	/* Otherwise recurse on all subnodes and return a total.	*/
	count = 0;
	for (i = 0; i < subtree->num_subnodes; i++) {
		num_leaves = charm_count_policy_leaves(subtree->subnode[i]);
		if (num_leaves == 0) {
			return 0;	/* error case.	*/
		} else {
			count += num_leaves;
		}
	}
	
	return count;
}

/***************************************************************************
 * Policy manipulation
 ***************************************************************************/

/*!
 * Create a policy leaf subnode from an attribute string.
 *
 * @param attribute_str			Attribute string.
 * @return						Allocated policy subnode.
 */

charm_attribute_subtree*
charm_policy_create_leaf(char *attribute_str)
{
	charm_attribute_subtree *leaf;
	
	/* Make sure there's room for the string.	*/
	if ((strlen(attribute_str) + 1) > MAX_ATTRIBUTE_STR) {
		return NULL;
	}
	
	/* Allocate and clear the subtree.		*/
	leaf = SAFE_MALLOC(sizeof(charm_attribute_subtree));
	if (leaf == NULL) {
		return NULL;
	}
	memset(leaf, 0, sizeof(charm_attribute_subtree));
	
	/* Copy the string into the attribute and set up the node.	*/
//	printf("%s: input    => '%s'\n", __FUNCTION__, attribute_str);
//	printf("%s: leaf_ptr => '%s'\n", __FUNCTION__, leaf->attribute.attribute_str);
	strcpy((char*)leaf->attribute.attribute_str, attribute_str);
	
	/* look for presence of '!' (not) */
	if(attribute_str[0] == '!') {
		leaf->attribute.is_negated = TRUE;
	}
	
	leaf->node_type = CHARM_ATTRIBUTE_POLICY_NODE_LEAF;
	
	return leaf;
}

/*!
 * Create a policy subnode from an array of subnodes.
 *
 * @param node_type			CHARM_ATTRIBUTE_NODE_TYPE value.
 * @param num_subnodes		Number of subnodes in the array.
 * @param threshold_k		Threshold value k.
 * @param subnodes			Array of charm_attribute_subtree pointers.
 * @return					Allocated policy subnode.
 */

charm_attribute_subtree*
charm_policy_create_node(CHARM_ATTRIBUTE_NODE_TYPE node_type, uint32 num_subnodes, uint32 threshold_k, charm_attribute_subtree **subnodes)
{
	charm_attribute_subtree *node;
	uint32 i;
	
	/* Allocate and clear the subtree.		*/
	node = SAFE_MALLOC(sizeof(charm_attribute_subtree));
	if (node == NULL) {
		return NULL;
	}
	memset(node, 0, sizeof(charm_attribute_subtree));
	
	/* Copy the string into the attribute and set up the node.	*/
	node->node_type = node_type;
	node->num_subnodes = num_subnodes;
	node->threshold_k = threshold_k;
	
	if (num_subnodes > 0) {
		node->subnode = SAFE_MALLOC(num_subnodes * sizeof(charm_attribute_subtree *));
		if (node->subnode == NULL) {
			free(node); /* out of memory */
			return NULL;
		}
	
		for (i = 0; i < num_subnodes; i++) {
			node->subnode[i] = subnodes[i];
		}
	}
			
	return node;
}

/*!
 * Recursively compact a tree structure.  This consists of combining parent
 * and child nodes where appropriate. 
 *
 * The process is nicked from John Bethencourt's library, though the code isn't.
 *
 * @param subtree			The subtree.
 */

void
charm_policy_compact(charm_attribute_subtree* subtree)
{
	uint32 i;
	
	/* First compact all of the subnodes.				*/
	for (i = 0; i < subtree->num_subnodes; i++) {
		charm_policy_compact(subtree->subnode[i]);
	}
	
	/* Initiate merging if this is an OR or AND node.	*/
	if (subtree->node_type == CHARM_ATTRIBUTE_POLICY_NODE_AND ||
		subtree->node_type == CHARM_ATTRIBUTE_POLICY_NODE_OR)	{
		/* Merge every subnode that has the same node type.		*/
		for (i = 0; i < subtree->num_subnodes; i++) {
			if (subtree->subnode[i]->node_type == subtree->node_type) {
				/* Merge the parent with this subnode.	*/
				charm_policy_merge_child(subtree, i);
			}
		}
	}
}

/*!
 * Merge a child into the subtree.  Only works if the parent and child
 * node are both OR nodes or both AND nodes.
 *
 * @param subtree			The subtree.
 * @param child_num			Index of the child.
 */

void
charm_policy_merge_child(charm_attribute_subtree* subtree, uint32 child_num)
{
	uint32 new_num_nodes, i;
	charm_attribute_subtree *child_subtree;
	
	if (subtree->node_type != subtree->subnode[child_num]->node_type) {
		//LOG_ERROR("charm_policy_compact: Node types don't match");
	}
	
	/* Merge the attribute list from the child into the parent node;
	 * remove the child from the parent node's list.
	 * 
	 * This is ugly.  Would be so much easier if we used a proper structured
	 * array type.  */
	new_num_nodes = (subtree->num_subnodes + subtree->subnode[child_num]->num_subnodes) - 1;
	child_subtree = subtree->subnode[child_num];
	
	/* Re-allocate the array to contain the correct number of elements.	*/
	subtree->subnode = charm_policy_extend_array(subtree->subnode, subtree->num_subnodes, new_num_nodes);
	
	/* Move all of the subnodes from the child into the parent node.	*/
	for (i = 0; i < child_subtree->num_subnodes; i++) {
		/* Put the first of the child's subnode in the slot where the child used to live.	*/
		if (i == 0) {
			subtree->subnode[child_num] = child_subtree->subnode[i];
		} else {			
			/* Put the rest into the high end of the array.					*/
			subtree->subnode[subtree->num_subnodes + (i - 1)] = child_subtree->subnode[i];
		}
	}
	subtree->num_subnodes = new_num_nodes;
	
	/* Now get rid of the child subnode.	*/
	child_subtree->num_subnodes = 0;
	charm_attribute_subtree_clear(child_subtree);
	SAFE_FREE(child_subtree);
}

/*!
 * Extend an array of charm_attribute_subtree pointers.
 *
 * @param attributes		The original array.
 * @param old_nodes			Number of nodes in the original array.
 * @param new_nodes			Desired number of nodes.
 */

charm_attribute_subtree **
charm_policy_extend_array(charm_attribute_subtree **attributes, uint32 old_nodes, uint32 new_nodes)
{
	uint32 i;
	charm_attribute_subtree **new_attributes;
	
	if (new_nodes <= old_nodes) {
		return attributes;
	}
	
	new_attributes = SAFE_MALLOC(new_nodes * sizeof(charm_attribute_subtree*));
	memset(new_attributes, 0, new_nodes * sizeof(charm_attribute_subtree*));
	
	for (i = 0; i < old_nodes; i++) {
		new_attributes[i] = attributes[i];
	}
	
	if (old_nodes > 0) {
		SAFE_FREE(attributes);
	}
	
	return new_attributes;
}

/*!
 * Parse a string to obtain an attribute policy.
 *
 * @param policy		A charm_attribute_policy structure.
 * @param policy_str	The policy string.
 * @param CHARM_ERROR_NONE or an error code
 */

CHARM_ERROR charm_policy_from_string(charm_attribute_policy *policy, char *policy_str)
{
	charm_attribute_subtree* subtree = NULL;

	memset(policy, 0, sizeof(charm_attribute_policy));
	
	subtree = parse_policy_lang( policy_str );
	policy->root = subtree;
	policy->str = strdup(policy_str);
	return CHARM_ERROR_NONE;
}

/*!
 * Parse attribute policy to obtain the string.
 *
 * @param policy		A charm_attribute_policy structure.
 * @param string or NULL if policy structure is empty.
 */

char*
charm_get_policy_string(charm_attribute_policy *policy)
{
	if(policy == NULL) {
		goto cleanup;
	}
	else if(policy->str != NULL)
		/* if string pointer set already, just return */
		return policy->str;
	else {
		/* TODO: parse the policy structure and convert into a string */
	}
cleanup:
	return NULL;
}

/* Returns the number of bits necessary represent integer in binary */ 
int num_bits(int value)
{
	int j;
	
	for(j = 0; j < BITS; j++) {
		if(value < pow(2,j)) {
			double x = (double)j;
			// round to nearest multiple of 4
			int newj = (int) ceil(x/4)*4;
			// printf("numberOfBits => '%d'\n", newj);
			return newj;
		}
	}
	return 0;
}

/*!
 * This recursive function counts the total number of leaves in a policy.
 *
 * @param charm_attribute_subtree	Pointer to a charm_attribute_subtree structure.
 * @return							Total number of leaves.
 */

uint32 prune_tree(charm_attribute_subtree *subtree, charm_attribute_list *attribute_list)
{
	uint32 k, i, j, result=0;
	int32 attribute_index;
	uint32 num_satisfied_subnodes;
	uint32 *satisfied_leaves = NULL;
	uint32 smallest_node, smallest_node_count;

	if (subtree == NULL) {
		printf("prune_tree: encountered NULL policy subtree.\n");
		//LOG_ERROR("prune_tree: encountered NULL policy subtree");
		return 0;
	}

	/* There are four different cases we must deal with: leaf nodes, and three types of gate.	*/
	switch(subtree->node_type) {
		case CHARM_ATTRIBUTE_POLICY_NODE_LEAF:
			/* Search the attribute list for a match.	*/
			attribute_index = charm_get_attribute_index_in_list(&(subtree->attribute), attribute_list);
			//printf("subtree->attribute: %s\n", subtree->attribute.attribute_str);
			//printf("attribute_index: %d\n", attribute_index);
			/* If the node is /not/ primed (negated), return whether or not it was found.  Otherwise return
			 * the opposite. Either way this will end the recursion. */
			result = 0;
			if ((attribute_index >= 0) && !(subtree->is_negated)) { result = 1; }
			if ((attribute_index < 0) && subtree->is_negated) { result = 1; }

			return result;

		case CHARM_ATTRIBUTE_POLICY_NODE_AND:
			/* AND gates are N-of-N threshold gates */
			k = subtree->num_subnodes;
			//printf("found AND node: %d\n", (int) k);
			break;

		case CHARM_ATTRIBUTE_POLICY_NODE_OR:
			/* OR gates are 1-of-N threshold gates	*/
			k = 1;
			break;

		case CHARM_ATTRIBUTE_POLICY_NODE_THRESHOLD:
			/* THRESHOLD gates have a k parameter associated with them. */
			k = subtree->threshold_k;
			break;

		default:
			//LOG_ERROR("prune_tree: encountered unknown gate type");
			printf("prune_tree: encountered unknown gate type.\n");
			return FALSE;
	}

	satisfied_leaves = (uint32*)SAFE_MALLOC(sizeof(uint32) * subtree->num_subnodes);

	/* Recurse on each subnode to determine the number of satisfied leaves hanging underneath it.	*/
	num_satisfied_subnodes = 0;
	for (i = 0; i < subtree->num_subnodes; i++) {
		/* Recurse on each subnode.  This will record the number of satisfied leaves inside of the node.
		 * At this point we also initialize each subnode as unused --- we'll mark the ones we
		 * /do/ want to use a bit later.	*/


		subtree->subnode[i]->use_subnode = FALSE;
		satisfied_leaves[i] = prune_tree(subtree->subnode[i], attribute_list);
		//printf("RESULT: i:%d => '%d'\n", i, satisfied_leaves[i]);
		/* Count the total number satisfied.	*/
		if (satisfied_leaves[i] > 0) {
			num_satisfied_subnodes++;
		}
	}

	//printf("RESULT: final num_satisfied_subnodes: '%d'\n", num_satisfied_subnodes);

	/* Make sure at least k of the subnodes are satisfied. 	*/
	if (num_satisfied_subnodes < k) {
		/* Not enough; mark this subtree as a dud.	*/
		subtree->use_subnode = FALSE;
		goto cleanup;
	}

	/* Consider the following cases:		*/
	result = 0;
	if (k == subtree->num_subnodes) {
		/* 1. k==N (AND gate): we need all of the subnodes.
		 * Mark all of the subnodes as necessary, and total them up.	*/
		for (i = 0; i < subtree->num_subnodes; i++) {
			subtree->subnode[i]->use_subnode = TRUE;
			result += satisfied_leaves[i];
		}
	} else {
		/* 2. OR or generic threshold gate.		*/
		/* Hunt for the k values with the smallest number of leaves.	*/
		for (j = 0; j < k; j++) {
			/* Find the smallest non-zero value in the list.	*/
			smallest_node = 0;
			smallest_node_count = 400000;
			for (i = 0; i < subtree->num_subnodes; i++) {
				if (satisfied_leaves[i] != 0 && satisfied_leaves[i] <= smallest_node_count)	{
					smallest_node_count = satisfied_leaves[i];
					smallest_node = i;
				}
			}

			/* Sanity check.	*/
			if (smallest_node_count >= 400000) {
				result = 0;
				goto cleanup;
			}

			/* Mark the node.	*/
			subtree->subnode[smallest_node]->use_subnode = TRUE;
			satisfied_leaves[smallest_node] = 0;
			result += smallest_node_count;
		}
	}

cleanup:
	if (satisfied_leaves != NULL) {
		SAFE_FREE(satisfied_leaves);
	}

	return result;
}

//CHARM_ERROR charm_get_pruned_attributes(charm_attribute_subtree *subtree, charm_attribute_list *attribute_list, uint32 *index)
//{
//	CHARM_ERROR err_code;
//	uint32 k, i;
//	/* There are four different cases we must deal with: leaf nodes, and three types of gate.	*/
//	switch(subtree->node_type) {
//		case CHARM_ATTRIBUTE_POLICY_NODE_LEAF:
//			if(subtree->use_subnode == TRUE) {
////				printf("FOUND A MATCH: '%s'\n", subtree->attribute.attribute_str);
//				strncpy((char *) attribute_list->attribute[*index].attribute_str, (char *) subtree->attribute.attribute_str, MAX_ATTRIBUTE_STR);
//				*index += 1;
////				subtree->use_subnode = FALSE; /* reset? */
//			}
//			return CHARM_ERROR_NONE;
//
//		case CHARM_ATTRIBUTE_POLICY_NODE_AND:
//			/* AND gates are N-of-N threshold gates */
//			k = subtree->num_subnodes;
//			break;
//
//		case CHARM_ATTRIBUTE_POLICY_NODE_OR:
//			/* OR gates are 1-of-N threshold gates	*/
//			k = 1;
//			break;
//
//		case CHARM_ATTRIBUTE_POLICY_NODE_THRESHOLD:
//			/* THRESHOLD gates have a k parameter associated with them. */
//			k = subtree->threshold_k;
//			break;
//
//		default:
//			//LOG_ERROR("prune_tree: encountered unknown gate type");
//			printf("%s: encountered unknown gate type.\n", __FUNCTION__);
//			return FALSE;
//	}
//
//	for (i = 0; i < k; i++) {
//		/* Recurse on each subnode.  This will record the number of satisfied leaves inside of the node.
//		 * At this point we also initialize each subnode as unused --- we'll mark the ones we
//		 * /do/ want to use a bit later.	*/
//		err_code = charm_get_pruned_attributes(subtree->subnode[i], attribute_list, index);
//		//printf("RESULT: i:%d => '%d'\n", i, satisfied_leaves[i]);
//	}
//
//	return CHARM_ERROR_NONE;
//}

CHARM_ERROR charm_get_pruned_attributes(charm_attribute_subtree *subtree, charm_attribute_list *attribute_list, uint32 *index)
{
	CHARM_ERROR err_code;
	uint32 i;
	if (subtree == NULL) {
		//LOG_ERROR("charm_count_policy_leaves: encountered NULL policy subtree");
		return CHARM_ERROR_INVALID_INPUT;
	}

	/* If it's a leaf, return 1.	*/
	if (subtree->node_type == CHARM_ATTRIBUTE_POLICY_NODE_LEAF) {
		if(subtree->use_subnode == TRUE) {
//				printf("FOUND A MATCH: '%s'\n", subtree->attribute.attribute_str);
			strncpy((char *) attribute_list->attribute[*index].attribute_str, (char *) subtree->attribute.attribute_str, MAX_ATTRIBUTE_STR);
			*index += 1;
//				subtree->use_subnode = FALSE; /* reset? */
		}
		return CHARM_ERROR_NONE;
	}

	/* If it's not a leaf node, there should be something under it.  Sanity check.	*/
	if (subtree->num_subnodes < 1) {
		//LOG_ERROR("charm_count_policy_leaves: encountered non-leaf subtree with no children");
		return CHARM_ERROR_INVALID_INPUT;
	}

	/* Otherwise recurse on all subnodes. */
	for (i = 0; i < subtree->num_subnodes; i++) {
		err_code = charm_get_pruned_attributes(subtree->subnode[i], attribute_list, index);
		if(err_code != CHARM_ERROR_NONE) {
			return err_code;
		}
	}

	return CHARM_ERROR_NONE;
}


CHARM_ERROR charm_get_policy_leaves(charm_attribute_subtree *subtree, charm_attribute_list *attribute_list, uint32 *index)
{
	uint32 i;
	if (subtree == NULL) {
		//LOG_ERROR("charm_count_policy_leaves: encountered NULL policy subtree");
		return CHARM_ERROR_INVALID_INPUT;
	}

	/* If it's a leaf, return 1.	*/
	if (subtree->node_type == CHARM_ATTRIBUTE_POLICY_NODE_LEAF) {
		strncpy((char *) attribute_list->attribute[*index].attribute_str, (char *) subtree->attribute.attribute_str, MAX_ATTRIBUTE_STR);
		*index += 1;
		return CHARM_ERROR_NONE;
	}

	/* If it's not a leaf node, there should be something under it.  Sanity check.	*/
	if (subtree->num_subnodes < 1) {
		//LOG_ERROR("charm_count_policy_leaves: encountered non-leaf subtree with no children");
		return CHARM_ERROR_INVALID_INPUT;
	}

	/* Otherwise recurse on all subnodes. */
	for (i = 0; i < subtree->num_subnodes; i++) {
		charm_get_policy_leaves(subtree->subnode[i], attribute_list, index);
	}

	return CHARM_ERROR_NONE;
}


void debug_print_policy(charm_attribute_policy *policy)
{
	int len = MAX_POLICY_STR * 2;
	char *pol_str = (char *) malloc(len);
	memset(pol_str, 0, len);
	charm_attribute_policy_to_string(policy->root, pol_str, len);
	printf("DEBUG: Policy -- '%s'\n", pol_str);
	free(pol_str);
}

void debug_print_attribute_list(charm_attribute_list *attribute_list)
{
	size_t len = MAX_POLICY_STR * 2;
	char *attr_str = (char *) malloc(len);
	memset(attr_str, 0, len);
	size_t result_len;
	charm_attribute_list_to_buffer(attribute_list, (unsigned char*)attr_str, len, &result_len);
	printf("DEBUG: Attribute list -- '%s'\n", attr_str);
	free(attr_str);
}

