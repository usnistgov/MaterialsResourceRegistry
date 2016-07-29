#include <string>
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

class error_handler: public DOMErrorHandler
{
public:
	error_handler () : failed_ (false) {}

	bool failed () const { return failed_; }

	string errors() {return errors_;}

	virtual bool handleError (const xercesc::DOMError&);

private:
  	bool failed_;
	string errors_ ;
};


bool error_handler::handleError (const xercesc::DOMError& e)
{
	bool warn (e.getSeverity() == DOMError::DOM_SEVERITY_WARNING);

	if (!warn)
		failed_ = true;

	DOMLocator* loc (e.getLocation ());

	char* uri (XMLString::transcode (loc->getURI ()));
	char* msg (XMLString::transcode (e.getMessage ()));

	stringstream ss;
	ss << loc->getLineNumber () << ":"; //<< loc->getColumnNumber () << " ";
	ss << (warn ? "warning: " : "error: ") << msg << "<br/>";
	string error = ss.str();
	
	errors_ += error;

	XMLString::release (&uri);
	XMLString::release (&msg);

	return true;
}


DOMLSParser* create_parser (XMLGrammarPool* pool)
{
	const XMLCh ls_id [] = {chLatin_L, chLatin_S, chNull};

	DOMImplementation* impl (
		DOMImplementationRegistry::getDOMImplementation (ls_id));

	DOMLSParser* parser (
		impl->createLSParser (
		DOMImplementationLS::MODE_SYNCHRONOUS,
		0,
		XMLPlatformUtils::fgMemoryManager,
		pool));

	DOMConfiguration* conf (parser->getDomConfig ());

	// Commonly useful configuration.
	conf->setParameter (XMLUni::fgDOMComments, false);
	conf->setParameter (XMLUni::fgDOMDatatypeNormalization, true);
	conf->setParameter (XMLUni::fgDOMEntities, false);
	conf->setParameter (XMLUni::fgDOMNamespaces, true);
	conf->setParameter (XMLUni::fgDOMElementContentWhitespace, false);

	// Enable validation.
	conf->setParameter (XMLUni::fgDOMValidate, true);
	conf->setParameter (XMLUni::fgXercesSchema, true);
	conf->setParameter (XMLUni::fgXercesSchemaFullChecking, true);

	// Use the loaded grammar during parsing.
	conf->setParameter (XMLUni::fgXercesUseCachedGrammarInParse, true);

	// Don't load schemas from any other source (e.g., from XML document's
	// xsi:schemaLocation attributes).
	conf->setParameter (XMLUni::fgXercesLoadSchema, false);

	// Xerces-C++ 3.1.0 is the first version with working multi
	// import support.
	#if _XERCES_VERSION >= 30100
	conf->setParameter (XMLUni::fgXercesHandleMultipleImports, true);
	#endif

	// We will release the DOM document ourselves.
	conf->setParameter (XMLUni::fgXercesUserAdoptsDOMDocument, true);

	return parser;
}


string _validate_xsd(const char * xsd){
	XMLPlatformUtils::Initialize ();

	error_handler eh;
	bool load_error = false;
	bool parse_error = false;

	MemoryManager* mm (XMLPlatformUtils::fgMemoryManager);

	// Load the schemas into grammar pool.
	{
		DOMLSParser* parser (create_parser (0));
		
		parser->getDomConfig ()->setParameter (XMLUni::fgDOMErrorHandler, &eh);

		Wrapper4InputSource xsd_source (new MemBufInputSource((const XMLByte *)  (xsd), strlen(xsd), "schema.xsd"));
		if (!parser->loadGrammar (&xsd_source, Grammar::SchemaGrammarType, true))
		{
			load_error = true;
		}
		if (eh.failed ())
		{
			parse_error = true;
		}
		parser->release ();
	}
	XMLPlatformUtils::Terminate ();

	if (load_error){
		return "Failed to load the file";
	}else if (parse_error){
		return eh.errors();		
	}
	return "";
}



string _validate_xml(const char * xsd,const char * xml){
	error_handler eh_xml;

	XMLPlatformUtils::Initialize ();
	{
		MemoryManager* mm (XMLPlatformUtils::fgMemoryManager);
		auto_ptr<XMLGrammarPool> gp (new XMLGrammarPoolImpl (mm));
		// Parse the XSD file.
		{
			error_handler eh_xsd;
			bool load_error = false;
			bool parse_error = false;

			// Load the schemas into grammar pool.
			{
				DOMLSParser* parser (create_parser (gp.get ()));
		
				parser->getDomConfig ()->setParameter (XMLUni::fgDOMErrorHandler, &eh_xsd);

				Wrapper4InputSource xsd_source (new MemBufInputSource((const XMLByte *)  (xsd), strlen(xsd), "schema.xsd"));
				if (!parser->loadGrammar (&xsd_source, Grammar::SchemaGrammarType, true))
				{
					load_error = true;
				}
				if (eh_xsd.failed ())
				{
					parse_error = true;
				}
				parser->release ();
			}

			if (load_error){
				return "Failed to load the file";
			}else if (parse_error){
				return eh_xsd.errors();		
			}
		}
		// Lock the grammar pool. 
		gp->lockPool ();
		// Parse the XML document.
		DOMLSParser* parser (create_parser (gp.get()));
	
		parser->getDomConfig ()->setParameter (XMLUni::fgDOMErrorHandler, &eh_xml);

		Wrapper4InputSource xml_source (new MemBufInputSource((const XMLByte *)  (xml), strlen(xml), "data.xml"));
	
		DOMDocument* doc (parser->parse (&xml_source));

		if (doc)
			doc->release ();

		parser->release ();
	}
	XMLPlatformUtils::Terminate ();

	if (eh_xml.failed ())
	{
		return eh_xml.errors();
	}
	return "";
}


char* validate_xsd(const char* xsd)
{
	string errors = _validate_xsd(xsd);
	char* c_errors = new char[errors.length() + 1];
	strcpy(c_errors, errors.c_str());
	return c_errors;
}

char* validate_xml(const char* xsd, const char* xml)
{
	string errors = _validate_xml(xsd, xml);
	char* c_errors = new char[errors.length() + 1];
	strcpy(c_errors, errors.c_str());
	return c_errors;
}

int main(){
	const char* xsd = "<xs:schema xmlns=\"http://www.w3.org/2001/XMLSchema\" xmlns:xs=\"http://www.w3.org/2001/XMLSchema\" xmlns:ns=\"namespace\" targetNamespace=\"namespace\" elementFormDefault=\"unqualified\" attributeFormDefault=\"unqualified\"> <xs:complexType name=\"Resource\"> 	<xs:sequence> <xs:element name=\"name\" type=\"xs:int\"/> </xs:sequence> </xs:complexType> </xs:schema>";

	const char* xml = "<Resource xmns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:ns=\"namespace\" xsi:type=\"ns:Resource\"> <name>3</name></Resource>";
	
	string errors_xsd = validate_xsd(xsd);
	cout << "ERRORS" << endl;
	cout << endl;
	cout << "XSD:" << endl;
	cout << errors_xsd;
	// Print Errors from the XSD file
	cout << endl;
	string errors_xml = validate_xml(xsd, xml);
	cout << "XML:" << endl;
	// Print Errors from the XML file
	cout << errors_xml;
	cout << endl;
	cout << "END" << endl;
	return 0;
}
