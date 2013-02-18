#include "SecretUtil.h"

Policy::Policy()
{
	p = NULL;
	isInit = false;
}

Policy::Policy(string str)
{
	p = charm_create_func_input_for_policy((char *) str.c_str());
	isInit = true;
}

Policy::Policy(const Policy& pol)
{
	/* copy constructor */
	Policy pol2 = pol;

	if(p == NULL) {
		p = (charm_attribute_policy *) SAFE_MALLOC(sizeof(charm_attribute_policy));
		isInit = false;
	}

	memcpy(p, pol2.p, sizeof(charm_attribute_policy));
	isInit = pol2.isInit;
}

Policy::~Policy()
{
	/* move to Policy class */
	if(isInit) {
		SAFE_FREE(p->str);
			uint32 i;
			for(i = 0; i < p->root->num_subnodes; i++) {
				charm_attribute_subtree_clear(p->root->subnode[i]);
				SAFE_FREE(p->root->subnode[i]);
			}
		SAFE_FREE(p->root->subnode);
		SAFE_FREE(p->root);
		SAFE_FREE(p);
	}
}

Policy& Policy::operator=(const Policy& pol)
{
	if(this == &pol)
		return *this;

	if(p != NULL) {
		SAFE_FREE(p->str);
			uint32 i;
			for(i = 0; i < p->root->num_subnodes; i++) {
				charm_attribute_subtree_clear(p->root->subnode[i]);
				SAFE_FREE(p->root->subnode[i]);
			}
		SAFE_FREE(p->root->subnode);
		SAFE_FREE(p->root);
		SAFE_FREE(p);
	}

	p = charm_create_func_input_for_policy(pol.p->str);
	isInit = true;
	return *this;

}

ostream& operator<<(ostream& s, const Policy& pol)
{
	s << charm_get_policy_string(pol.p);
	return s;
}

SecretUtil::SecretUtil()
{
}

SecretUtil::~SecretUtil()
{
}

Policy SecretUtil::createPolicy(string s)
{
//	Policy pol(s);
//	charm_policy_from_string(pol.p, (char *) s.c_str());
//	cout << "DEBUG: policy string: " << charm_get_policy_string(pol.p) << endl;
//	pol.isInit = true;
	return Policy(s);
}

CharmListStr SecretUtil::prune(Policy& pol, CharmListStr attrs)
{
	// copy
	string str = "(";
	for(int i = 0; i < attrs.length(); i++) {
		str += attrs[i] + ",";
	}
	str.erase(str.size()-1);
	str += ")";
	//cout << "ATTR string: " << str << endl;

	int str_size = str.size();
	char attributes[str_size+1];
	memset(attributes, 0, str_size);
	memcpy(attributes, (char *) str.c_str(), str_size);
	charm_attribute_list *attribute_list = charm_create_func_input_for_attributes(attributes);

//	debug_print_attribute_list(attribute_list);
//	charm_attribute_policy *charm_policy = charm_create_func_input_for_policy(pol.p->str);
//	debug_print_policy(charm_policy);
	uint32 leaves = prune_tree(pol.p->root, attribute_list);

	CharmListStr s;
	if(leaves == 0) {
		cout << "Insufficient attributes to satisfy policy." << endl;
		return s;
	}

	// walk pol.p->root and extract the use_subnode=TRUE
	charm_attribute_list *pruned_list = (charm_attribute_list *) SAFE_MALLOC(sizeof(charm_attribute_list));
	uint32 index = 0, i;
	charm_attribute_list_initialize(pruned_list, leaves);

	charm_get_pruned_attributes(pol.p->root, pruned_list, &index);
	if(index != leaves) {
		cout << "ERROR: Could not find all the pruned attributes: actual=" << index << ", expected=" << leaves << endl;
	}

	for(i = 0; i < index; i++) {
		s.append( (const char *) pruned_list->attribute[i].attribute_str );
	}

	charm_attribute_list_free(pruned_list);
	charm_attribute_list_free(attribute_list);
	return s;
}

CharmListStr SecretUtil::getAttributeList(Policy & pol)
{
	charm_attribute_list *attr_list = (charm_attribute_list *) SAFE_MALLOC(sizeof(charm_attribute_list));
	uint32 leaves = charm_count_policy_leaves(pol.p->root);
	uint32 index = 0, i;

	charm_attribute_list_initialize(attr_list, leaves);
	charm_get_policy_leaves(pol.p->root, attr_list, &index);
	CharmListStr attrList;
	if(index != leaves) {
		cout << "ERROR: could not extract attributes from policy tree." << endl;
		return attrList; // TODO: need to perform proper error handling
	}
	for(i = 0; i < index; i++) {
		attrList.append( (const char *) attr_list->attribute[i].attribute_str );
	}

	charm_attribute_list_free(attr_list);
	return attrList;
}

/*
 * Evaluate a polynomial: arguments are a list of coefficients and the value of x to evaluate
 */
ZR _evalPoly(PairingGroup & group, CharmListZR & coeff, ZR & x)
{
	int i, len = coeff.length();
	ZR share(0);
	for(i = 0; i < len; i++) {
		share = group.add(share, group.mul(coeff[i], group.exp(x, i)));
	}
	return share;
}

/*
 * Standard secret sharing: generates shares for a secret given the threshold, k,
 * and the number of participants, n.
 */
CharmListZR _genShares(PairingGroup & group, ZR secret, int k, int n)
{
	int i;
	CharmListZR a, shares;
	ZR z;
	if(k <= n) {
		a[0] = secret; // F(0) = secret
		for(i = 1; i < k; i++) {
			a[i] = group.random(ZR_t);
		}

		for(i = 0; i <= n; i++) {
			z = ZR(i);
			shares[i] = _evalPoly(group, a, z);
		}
	}

	return shares;
}

CharmListZR _genSharesForGivenX(PairingGroup & group, ZR secret, CharmListZR & q, CharmListZR & x)
{
	int i, n = x.length();
	CharmListZR shares;

	for(i = 0; i <= n; i++) {
		shares[i] = _evalPoly(group, q, x[i]);
	}

	return shares;
}


CharmListZR SecretUtil::genShares(PairingGroup & group, ZR secret, int k, int n)
{
	return _genShares(group, secret, k, n);
}

CharmListZR SecretUtil::genSharesForX(PairingGroup & group, ZR secret, CharmListZR & q, CharmListZR & x)
{
	return _genSharesForGivenX(group, secret, q, x);
}

/*
 * Computes secret sharing over a tree utilizing the above functions.
 */
CHARM_ERROR _computeSharesOverTree(PairingGroup & group, ZR secret, charm_attribute_subtree *subtree, CharmDictZR & dict)
{
	CHARM_ERROR err_code;
	uint32 k, i;
	string attr;
	switch(subtree->node_type) {
		case CHARM_ATTRIBUTE_POLICY_NODE_LEAF:
				attr = string((char *) subtree->attribute.attribute_str);
				//cout << "store: k=" << attr << ", v=" << secret << endl;
				dict[ attr ] = secret;
			return CHARM_ERROR_NONE;

		case CHARM_ATTRIBUTE_POLICY_NODE_AND:
			/* AND gates are N-of-N threshold gates */
			k = subtree->num_subnodes;
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
			printf("%s: encountered unknown gate type.\n", __FUNCTION__);
			return CHARM_ERROR_INVALID_INPUT;
	}

	CharmListZR shares = _genShares(group, secret, k, (int) subtree->num_subnodes);
    //cout << "Shares:\n" << shares << endl;

	for (i = 0; i < subtree->num_subnodes; i++) {
		err_code = _computeSharesOverTree(group, shares[i+1], subtree->subnode[i], dict);
		if(err_code != CHARM_ERROR_NONE)
			return err_code;
	}

	return CHARM_ERROR_NONE;
}

CHARM_ERROR _computeSharesOverTree(PairingGroup & group, ZR secret, charm_attribute_subtree *subtree, CharmListZR & list)
{
	CHARM_ERROR err_code;
	uint32 k, i;
	string attr;
	switch(subtree->node_type) {
		case CHARM_ATTRIBUTE_POLICY_NODE_LEAF:
				attr = string((char *) subtree->attribute.attribute_str);
				//cout << "store: k=" << attr << ", v=" << secret << endl;
				list.insert(attr, secret);
			return CHARM_ERROR_NONE;

		case CHARM_ATTRIBUTE_POLICY_NODE_AND:
			/* AND gates are N-of-N threshold gates */
			k = subtree->num_subnodes;
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
			printf("%s: encountered unknown gate type.\n", __FUNCTION__);
			return CHARM_ERROR_INVALID_INPUT;
	}

	CharmListZR shares = _genShares(group, secret, k, (int) subtree->num_subnodes);
    //cout << "Shares:\n" << shares << endl;

	for (i = 0; i < subtree->num_subnodes; i++) {
		err_code = _computeSharesOverTree(group, shares[i+1], subtree->subnode[i], list);
		if(err_code != CHARM_ERROR_NONE)
			return err_code;
	}

	return CHARM_ERROR_NONE;
}


CharmDictZR SecretUtil::calculateSharesDict(PairingGroup & group, ZR secret, Policy& pol)
{
	CharmDictZR dict;
	_computeSharesOverTree(group, secret, pol.p->root, dict);
	return dict;
}

CharmListZR SecretUtil::calculateSharesList(PairingGroup & group, ZR secret, Policy& pol)
{
	CharmListZR list;
	_computeSharesOverTree(group, secret, pol.p->root, list);
	return list;
}

// with traditional ints
CharmListZR _computelagrangeBasisInt(PairingGroup & group, int list[], int length)
{
	CharmListZR coeffs;
	int i, ii, j, jj;
	for(i = 0; i < length; i++) {
		ZR result = 1;
		ii = list[i];
		for(j = 0; j < length; j++) {
			jj = list[j];
			if( ii != jj) {
				result = group.mul(result, group.div(group.sub(ZR(0), ZR(jj)), group.sub(ZR(ii), ZR(jj))));
			}
		}
		coeffs[ ii ] = result;
	}

	return coeffs;
}

// for ZR elements
CharmListZR _computelagrangeBasisZR(PairingGroup & group, CharmListZR & list)
{
	CharmListZR coeffs;
	CharmListStr strKeys = list.strkeys();
	int strSize = strKeys.length();
	int i, j, length = list.length();
	ZR ii, jj;
	for(i = 0; i < length; i++) {
		ZR result = 1;
		ii = list[i];
		for(j = 0; j < length; j++) {
			jj = list[j];
			if( ii != jj) {
				result = group.mul(result, group.div(group.sub(ZR(0), jj), group.sub(ii, jj)));
			}
		}
		if(strSize == 0) coeffs[ i ] = result;
		else coeffs.insert(i, result, strKeys[i]);
//		cout << "i=" << i << ", list[" << i << "]=" << list[i] << endl << ", " << coeffs[i] << endl;
	}

	return coeffs;
}

CHARM_ERROR _getCoefficients(PairingGroup & group, charm_attribute_subtree *subtree, ZR coeff_result, CharmDictZR & coeffDict)
{
	CHARM_ERROR err_code;
	uint32 k, i;
	string attr;
	switch(subtree->node_type) {
		case CHARM_ATTRIBUTE_POLICY_NODE_LEAF:
				attr = string((char *) subtree->attribute.attribute_str);
				//cout << "coeff: k=" << attr << ", v=" << coeff_result << endl;
				coeffDict[ attr ] = coeff_result;
			return CHARM_ERROR_NONE;

		case CHARM_ATTRIBUTE_POLICY_NODE_AND:
			/* AND gates are N-of-N threshold gates */
			k = subtree->num_subnodes;
			break;

		case CHARM_ATTRIBUTE_POLICY_NODE_OR:
			/* OR gates are 1-of-N threshold gates	*/
			k = 1;
			break;

//		case CHARM_ATTRIBUTE_POLICY_NODE_THRESHOLD:
//			/* THRESHOLD gates have a k parameter associated with them. */
//			k = subtree->threshold_k;
//			break;

		default:
			//LOG_ERROR("prune_tree: encountered unknown gate type");
			printf("%s: encountered unknown gate type.\n", __FUNCTION__);
			return CHARM_ERROR_INVALID_INPUT;
	}
	int list[k];
	for(i = 0; i < k; i++) list[i] = (i + 1);
    CharmListZR coeffs = _computelagrangeBasisInt(group, list, k); // for subtree nodes

	/* recursively apply to subtrees from 1 to n */
	for (i = 0; i < subtree->num_subnodes; i++) {
		if(subtree->node_type == CHARM_ATTRIBUTE_POLICY_NODE_AND) {
			err_code = _getCoefficients(group, subtree->subnode[i], coeff_result * coeffs[ list[i] ], coeffDict);
		}
		else if(subtree->node_type == CHARM_ATTRIBUTE_POLICY_NODE_OR) {
			err_code = _getCoefficients(group, subtree->subnode[i], coeff_result * coeffs[ list[0] ], coeffDict);
		}
		if(err_code != CHARM_ERROR_NONE)
			return err_code;

	}

	return CHARM_ERROR_NONE;

}

CharmDictZR SecretUtil::getCoefficients(PairingGroup & group, Policy& pol)
{
	CharmDictZR coeffDict;
	_getCoefficients(group, pol.p->root, ZR(1), coeffDict);
	return coeffDict;
}

CharmListZR SecretUtil::recoverCoefficientsDict(PairingGroup & group, CharmListZR & list)
{
	return _computelagrangeBasisZR(group, list);
}

CharmListZR SecretUtil::recoverCoefficientsDict(PairingGroup & group, CharmListInt & list)
{
	int newLen = list.length();
	int newList[ newLen ];
	for(int i = 0; i < newLen; i++) {
		newList[i] = list[i];
	}
	return _computelagrangeBasisInt(group, newList, newLen);
}

CharmListZR SecretUtil::intersectionSubset(PairingGroup & group, CharmListStr & w, CharmListStr & wPrime, int d)
{
    int wLen = w.length(), wPrimeLen = wPrime.length(), index = 0;
    CharmListZR S;
    ZR hash;

    for (int i = 0; i < wLen; i++)
    {
        for (int j = 0; j < wPrimeLen; j++)
        {
            if ( isEqual(w[i], wPrime[j]) )
            {
            	hash = group.hashListToZR(w[i]);
                S.insert(index, hash, w[i]);
                index++;
            }
        }
    }

    if(S.length() < d) {
    	cout << "Insufficient attributes in common to decrypt." << endl;
    	CharmListZR tmp;
    	return tmp; // return empty list
    }

    return S;
}

