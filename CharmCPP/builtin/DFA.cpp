#include "DFA.h"
#include <string>
#include <vector>
#include <iostream>
#include <fstream>

string pyDFA = "python callPyDFA.py";

DFA::DFA()
{
	tmpFile = "tmpFile.txt";

}

DFA::~DFA()
{

}

vector<string> &split(const string &s, char delim, vector<string> &elems) {
    stringstream ss(s);
    string item;
    while(getline(ss, item, delim)) {
        elems.push_back(item);
    }
    return elems;
}


vector<string> split(const string &s, char delim) {
    vector<string> elems;
    return split(s, delim, elems);
}

void getInts(string x, CharmListInt & A)
{
	vector<string> y = split(x, ':');
	for(int i = 0; i < (int) y.size(); i++) {
		if(isEqual(y[i], "")) continue;
		A[i] = atoi( y[i].c_str() );
	}
}

void DFA::getTheTransitions(CharmMetaListInt & theT, string line, int start_index)
{
	int index = start_index;
	vector<string> y = split(line, ':');
	for(int i = 0; i < (int) y.size(); i++) {
		CharmListInt t;
		vector<string> z = split(y[i], ',');
		if(z.size() == 3) {
			t[0] = atoi( z[0].c_str() );
			t[1] = atoi( z[1].c_str() );
			int k = alphabet.searchKey( z[2] );
			if (k != -1) t[2] = k;
			else cout << "ERROR: non-existent alphabet: " << k << " for " << z[2] << endl;
			theT[index] = t;
			index++;
		}
	}
}

void DFA::parseLine(string line)
{
	vector<string> x = split(line, '=');

	if(x.size() == 2) {
		if(isEqual(x[0], "Q")) {
			// cout << x[0] << " => " << x[1] << endl;
			getInts(x[1], Q);
			if(verbose) cout << "Q +>\n" << Q << endl;
		}
		else if(isEqual(x[0], "T")) {
			this->getTheTransitions(T, x[1], 0);
			if(verbose) cout << "T +>\n" << T << endl;
		}
		else if(isEqual(x[0], "F")) {
			getInts(x[1], F);
			if(verbose) cout << "F +>\n" << F << endl;
		}
		else if(isEqual(x[0], "q0")) {
			q0 = atoi( x[1].c_str() );
		}
	}
}

void DFA::constructDFA(string rexpr, string alpha)
{
	string cmd = pyDFA + " -c '" + rexpr + "' '" + alpha + "' '" + tmpFile + "'";
	regex = rexpr;
	alphabetStr = alpha;
	int alpha_len = (int) alpha.size();
	for(int i = 0; i < alpha_len; i++) {
		alphabet[i] = string(&alpha[i], 1);
	}

	system(cmd.c_str());

	// parse the tmpFile and print string
	string line;
	ifstream myfile(tmpFile.c_str());
	if (myfile.is_open())
	  {
		while ( myfile.good() )
		{
		  getline (myfile, line);
		  this->parseLine(line); // cout << line << endl; // parse each line
		}
		myfile.close();
	  }
	  else cout << "Unable to open file";

	return;
}

//Q = [0, 1, 2]
//T = [ (0, 1, 'a'), (1, 1, 'b'), (1, 2, 'a') ]
//q0 = 0
//F = [2]

bool DFA::accept(CharmListStr & w)
{
	string cmd = pyDFA + " -a '" + regex + "' '" + alphabetStr + "' '" + tmpFile + "' ";
	string s = "";
	for(int i = 0; i < (int) w.length(); i++) {
		s += w[i];
	}
	cmd += "'" + s + "'";
	system(cmd.c_str());

	string line;
	ifstream myfile(tmpFile.c_str());
	if (myfile.is_open())
	  {
		while ( myfile.good() )
		{
			getline (myfile, line);
			vector<string> x = split(line, '=');
			if(isEqual(x[0], "accept")) {
				int newx = atoi( x[1].c_str() );
				if(newx == 1) return true;
				else return false;
			}
		}
		myfile.close();
	  }
	  else cout << "Unable to open file";

	cout << "FAILED!!!!!" << endl;
	return false;
}

CharmListInt DFA::getStates()
{
	return Q;
}

CharmListStr DFA::getAlphabet()
{
	return alphabet;
}

int DFA::getAcceptState(CharmMetaListInt & t)
{
	stringstream ss;
	ss << "\"{";

	for(int i = 1; i <= (int) t.length(); i++) {
		ss << i << ":" << this->hashToKey(t[i]) << ", ";
	}
	ss << "}\"";
	string cmd = pyDFA + " -ga '" + regex + "' '" + alphabetStr + "' '" + tmpFile + "' " + ss.str();
	system(cmd.c_str());

	string line;
	ifstream myfile(tmpFile.c_str());
	if (myfile.is_open())
	  {
		while ( myfile.good() )
		{
			getline (myfile, line);
			vector<string> x = split(line, '=');
			if(isEqual(x[0], "x")) {
				int newx = atoi( x[1].c_str() );
				return newx;
			}
		}
		myfile.close();
	  }
	  else cout << "Unable to open file";


	return -1; // TODO: construct string to PyDFA and get response
}

CharmListInt DFA::getAcceptStates()
{
//	CharmListInt f;
//	f[0] = 2;
	return F;
}

CharmMetaListInt DFA::getTransitions()
{
	return T;
}

CharmMetaListInt DFA::getTransitions(CharmListStr & w)
{   // 1-indexed
	CharmMetaListInt t;
	string cmd = pyDFA + " -t '" + regex + "' '" + alphabetStr + "' '" + tmpFile + "' ";
	string s = "";
	for(int i = 0; i < (int) w.length(); i++) {
		s += w[i];
	}
	cmd += "'" + s + "'";
	system(cmd.c_str());

	string line;
	ifstream myfile(tmpFile.c_str());
	if (myfile.is_open())
	  {
		while ( myfile.good() )
		{
			getline (myfile, line);
			vector<string> x = split(line, '=');
			if(isEqual(x[0], "Ti")) {
				this->getTheTransitions(t, x[1], 1);
				if(verbose) cout << "getTransitions +>\n" << t << endl;
				return t;
			}
		}
		myfile.close();
	  }
	  else cout << "Unable to open file";

	return t; // empty list
}

string DFA::hashToKey(CharmListInt t)
{
	stringstream ss;
	string res;
	if (t[2] == -1) {
		return "";
	}
	ss << "(" << t[0] << "," << t[1] << ",'" << alphabet[ t[2] ] << "')";
	return ss.str();
}

string DFA::getString(string w)
{
	return w;
}

string DFA::getString(int w)
{
//	if (w == 97) {
//		return "a";
//	}
//	else if(w == 98) {
//		return "b";
//	}
	return alphabet[w];
}

CharmListStr DFA::getSymbols(string s) // convert "abc" to {1:"a", 2:"b", etc}
{
	CharmListStr s2;
	int index = 1;
	const char *tmp = s.c_str();
	for(int i = 0; i < (int) s.length(); i++) {
		s2.insert(index, string(&tmp[i], 1));
		index++;
	}
	return s2;
}
