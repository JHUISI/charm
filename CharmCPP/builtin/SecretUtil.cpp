#include "SecretUtil.h"

Policy::Policy()
{
	p = (charm_attribute_policy *) SAFE_MALLOC(sizeof(charm_attribute_policy));
	isInit = false;
}

Policy::Policy(const Policy& pol)
{
	/* copy constructor */
	Policy pol2 = pol;
	memcpy(p, pol2.p, sizeof(charm_attribute_policy));
	isInit = pol.isInit;
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
	}
	SAFE_FREE(p);
}

Policy& Policy::operator=(const Policy& pol)
{
	if(this == &pol)
		return *this;

	memset(p, 0, sizeof(charm_attribute_policy));
	memcpy(p, pol.p, sizeof(charm_attribute_policy));
	isInit = pol.isInit;
	return *this;

}

SecretUtil::SecretUtil()
{
}

SecretUtil::~SecretUtil()
{
}

Policy SecretUtil::createPolicy(string s)
{
	Policy pol;
	charm_policy_from_string(pol.p, (char *) s.c_str());
	cout << "DEBUG: policy string: " << charm_get_policy_string(pol.p) << endl;
	pol.isInit = true;
	return pol;
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
	cout << "ATTR string: " << str << endl;

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

//CharmDict SecretUtil::getCoefficients(Policy & pol)
//{
//	CharmDict dict;
//	return dict;
//}

