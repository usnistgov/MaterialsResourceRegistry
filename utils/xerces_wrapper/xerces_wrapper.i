/*validate.i*/
%module xerces_wrapper

%{
#include <memory>
#include <cstddef> 
#include <iostream>
#include <fstream>
#include <sstream>
#include <list>

#include <xercesc/util/XMLUni.hpp>
#include <xercesc/util/XMLString.hpp>
#include <xercesc/util/PlatformUtils.hpp>

#include <xercesc/dom/DOM.hpp>

#include <xercesc/validators/common/Grammar.hpp>
#include <xercesc/framework/XMLGrammarPoolImpl.hpp>

#include <xercesc/framework/MemBufInputSource.hpp>
#include <xercesc/framework/Wrapper4InputSource.hpp>

using namespace std;
using namespace xercesc;
char* validate_xsd(const char * xsd);
char* validate_xml(const char * xsd, const char * xml);
%}
char* validate_xsd(const char * xsd);
char* validate_xml(const char * xsd, const char * xml);

