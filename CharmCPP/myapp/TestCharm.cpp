#include "Charm.h"
#include <iostream>
#include <string>
using namespace std;

int main()
{
    PairingGroup group(MNT160);
    CharmList list, list2, list3;
    CharmListG1 g1List;
    G1 g1;
    G2 g2;
    GT gt;
    ZR a, b, c, d;
    a = group.random(ZR_t);
    b = group.random(ZR_t);
    g1 = group.random(G1_t);
    g2 = group.random(G2_t);
    gt = group.random(GT_t);
    cout << "a: " << a << endl;
    cout << "b: " << b << endl;

    SecretUtil util;
    CharmListStr attrs;
    attrs.append("ONE");
    attrs.append("TWO");
    attrs.append("THREE");
    attrs.append("FOUR");

    Policy p = util.createPolicy("((ONE or TWO) and THREE)");

    cout << "Policy: " << p << endl;
    CharmListStr pruned_list = util.prune(p, attrs);

    cout << "Pruned:\n" << pruned_list << endl;

    CharmListStr attr_list = util.getAttributeList(p);

    cout << "Attr list:\n" << attr_list << endl;

//    CharmListZR shares = util.genShares(group, a, 1, 2);
    ZR secret = a;
    CharmDictZR sh = util.calculateSharesDict(group, secret, p);
    cout << "Secret: " << secret << endl;
    cout << "Shares:\n" << sh << endl;

	CharmDictZR coeff = util.getCoefficients(group, p);

	cout << "Final coeff dict:\n" << coeff << endl;

//    CharmListStr listKeys;
//    listKeys.append("ONE");
//    listKeys.append("TWO");
//    int i, _list[] = {1, 2};
//    CharmListZR coeffs = util.computelagrangeBasis(group, _list, 2);
//
//    cout << "Coeffs list:\n" << coeffs << endl;

    // recover secret
//    ZR sec = 0;
//    for(i = 0; i < 2; i++) {
//    	sec = group.add(sec, group.mul(coeffs[ _list[i] ], sh[ listKeys[i] ]));
//    }
//    cout << "Recovered secret: " << sec << endl;


//    cout << "c: " << group.add(a, b) << endl;
//    cout << "d: " << group.sub(a, b) << endl;
//    cout << "e: " << group.mul(a, b) << endl;
//    cout << "f: " << group.div(a, b) << endl;
//    cout << "G1 Tests..." << endl;
//    cout << convert_str(g1) << endl;
//    cout << "G2 Tests..." << endl;
//    cout << convert_str(g2) << endl;
//
//    cout << "GT Tests..." << endl;
//    cout << convert_str(gt) << endl;
//    list.insert(0, "hello world");
//    list.insert(1, a);
//    list.insert(2, g1);
//    list.insert(3, g2);
//    list.insert(4, gt);
//    list2.insert(0, "hello world");
//    list2.insert(1, g1);
//    list2.insert(2, g1);
//    G1 testg1 = group.hashListToG1(list);
//    G2 testg2 = group.hashListToG2(list);
//    cout << "ZR hashList1 : " << group.hashListToZR(list) << endl;
//    cout << "ZR hashList2 : " << group.hashListToZR(list2) << endl;
//    cout << "G1 hashList1 : " << convert_str(testg1) << endl;
//    cout << "G2 hashList1 : " << convert_str(testg2) << endl;
//    string s1 = serialize(list[1]);
//    string s2 = serialize(list[2]);
//    string s3 = serialize(list[3]);
//    string s4 = serialize(list[4]);
//    cout << "Original ZR : " << list[1] << endl;
//    cout << "Serialize ZR : " << s1 << endl;
//    cout << "Serialize G1 : " << s2 << endl;
//    cout << "Serialize G2 : " << s3 << endl;
//    cout << "Serialize GT : " << s4 << endl;
//    Element e0, e1, e2, e3;
//    deserialize(e0, s1);
//    deserialize(e1, s2);
//    deserialize(e2, s3);
//    deserialize(e3, s4);
//    cout << "Deserialize ZR : " << e0 << endl;
//    cout << "Deserialize G1 : " << e1 << endl;
//    cout << "Deserialize G2 : " << e2 << endl;
//    cout << "Deserialize GT : " << e3 << endl;
//
//    list3.insert(0, testg1);
//    list3.insert(1, list);
//    list3.insert(2, testg2);
//
//    CharmList list4 = list3[1].getList();
//    cout << "\nCharmList Test list3\n" << list3 << endl;
//    cout << "\nCharmList Test list4\n" << list4 << endl;
//
//    cout << "list4 index 1: " << list4[1].getZR() << endl;

    /*
    a = 1024;
    cout << "ZR: " << a << endl;
    cout << "a << 8: " << (a << 8) << endl;
    cout << "a >> 8: " << (a >> 8) << endl;
    //c = ZR("60326500890243420035384875331943132341407341884156227172769759599775466331604");
    //d = ZR("4294967295");
    //cout << "c & d:     " << (c & d) << endl;

    cout << "Pairing test..." << endl;
    cout << convert_str(group.pair(g1, g2)) << endl;
    cout << "GT inf: ?" << endl;
    GT gt2 = group.exp(gt, -1);
    cout << convert_str(gt2) << endl;
    cout << endl;
    cout << convert_str(group.mul(gt, gt2)) << endl;
*/   
    return 0;
}
