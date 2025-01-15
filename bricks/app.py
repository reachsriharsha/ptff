

import pdfplumber
import re
import pandas as pd
from typing import Dict, List, Tuple, Optional

class RHPExtractor:
    def __init__(self, pdf_path: str):
        """Initialize the RHP extractor with PDF path."""
        self.pdf = pdfplumber.open(pdf_path)
        self.toc_mapping = self._create_section_mapping()
        #print(f"TOC Mapping: {self.toc_mapping}")
        for key in self.toc_mapping:
            print(key)
            print(self.toc_mapping[key])
        
    def _create_section_mapping(self) -> Dict[str, Tuple[int, int]]:
        """
        Create mapping of section titles to their page numbers based on TOC.
        Returns dict with section titles as keys and (start_page, end_page) as values.
        """
        section_pattern = r'^SECTION [IVX]+'
        sections = {}
        current_section = None
        page_numbers = []
        
        # Extract page numbers from TOC
        for page in self.pdf.pages[:20]:  # Usually TOC is in first few pages
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                for line in lines:
                    # Look for section headers and page numbers
                    if re.match(section_pattern, line):
                        if current_section and page_numbers:
                            #print(f"Found section: {current_section} \n in pages {page_numbers[-1]}")
                            sections[current_section] = page_numbers[-1]
                        only_section = re.sub(r'\.', '', line)
                        #current_section = line.strip()
                        #only_section is of format SECTION V – ABOUT THE COMPANY  106, 
                        #remove the last numerical part
                        only_section = re.sub(r'\d+', '', only_section)
                        current_section = only_section.strip()
                        #print(f"Found section: {current_section}")
                        page_numbers = []
                        ## Extract page number at end of line
                        match = re.search(r'\d+$', line)
                        if match:
                            one_less_page_no = int(match.group()) - 1
                            page_numbers.append(one_less_page_no)
                    
                    ## Extract page number at end of line
                    #match = re.search(r'\d+$', line)
                    #if match:
                    #    page_numbers.append(int(match.group()))
        
        return sections

    def extract_section_content(self, section_name: str) -> str:
        """
        Extract content from a specific section.
        Args:
            section_name: Name of the section to extract
        Returns:
            Extracted text content
        """
        if section_name not in self.toc_mapping:
            raise ValueError(f"Section {section_name} not found in TOC")
            
        start_page = self.toc_mapping[section_name]
        text_content = []
        
        current_page = start_page
        while current_page < len(self.pdf.pages):
            page = self.pdf.pages[current_page]
            text = page.extract_text()
            
            # Check if we've reached the next section
            if any(next_section in text for next_section in self.toc_mapping.keys()):
                if current_page > start_page:
                    break
                    
            text_content.append(text)
            current_page += 1
            
        return '\n'.join(text_content)

    def extract_tables_from_section(self, section_name: str) -> List[pd.DataFrame]:
        """
        Extract all tables from a specific section.
        Args:
            section_name: Name of the section to extract tables from
        Returns:
            List of pandas DataFrames containing the tables
        """
        if section_name not in self.toc_mapping:
            raise ValueError(f"Section {section_name} not found in TOC")
            
        start_page = self.toc_mapping[section_name]
        tables = []
        
        current_page = start_page
        while current_page < len(self.pdf.pages):
            page = self.pdf.pages[current_page]
            
            # Extract tables from the page
            page_tables = page.extract_tables()
            if page_tables:
                for table in page_tables:
                    # Convert to DataFrame and clean up
                    df = pd.DataFrame(table[1:], columns=table[0])
                    df = df.dropna(how='all').reset_index(drop=True)
                    tables.append(df)
            
            # Check if we've reached the next section
            text = page.extract_text()
            if any(next_section in text for next_section in self.toc_mapping.keys()):
                if current_page > start_page:
                    break
                    
            current_page += 1
            
        return tables

    def extract_financial_information(self) -> Dict[str, pd.DataFrame]:
        """
        Specific method to extract financial information tables.
        Returns:
            Dictionary with table names as keys and DataFrames as values
        """
        financial_sections = [
            "SUMMARY OF FINANCIAL INFORMATION",
            "RESTATED FINANCIAL INFORMATION",
            "OTHER FINANCIAL INFORMATION"
        ]
        
        financial_data = {}
        for section in financial_sections:
            if section in self.toc_mapping:
                tables = self.extract_tables_from_section(section)
                financial_data[section] = tables
                
        return financial_data

    def extract_risk_factors(self) -> List[str]:
        """
        Extract risk factors from the risk factors section.
        Returns:
            List of risk factors
        """
        risk_section = self.extract_section_content("SECTION III – RISK FACTORS")
        risk_factors = []
        
        # Split by numbers and clean up
        if risk_section:
            factors = re.split(r'\d+\.', risk_section)
            risk_factors = [factor.strip() for factor in factors if factor.strip()]
            
        return risk_factors

    def close(self):
        """Close the PDF file."""
        self.pdf.close()


def extract_rhp_data(pdf_path: str, sections_of_interest: List[str]) -> Dict:
    """
    Main function to extract data from RHP.
    Args:
        pdf_path: Path to the RHP PDF file
        sections_of_interest: List of section names to extract
    Returns:
        Dictionary containing extracted data
    """
    extractor = RHPExtractor(pdf_path)
    extracted_data = {}
    
    try:
        for section in sections_of_interest:
            #check if section is part of the key in extracted_data
            for key in extractor.toc_mapping:
                if section in key:
                    #extracted_data[section] = {
                    #extracted_data[key] = {
                    #    'text': extractor.extract_section_content(section),
                    #    'tables': extractor.extract_tables_from_section(section)
                    #}
                    extracted_data[key] = {
                        'text': extractor.extract_section_content(key),
                        'tables': extractor.extract_tables_from_section(key)
                    }
            
        # Special handling for financial information
        extracted_data['financial_information'] = extractor.extract_financial_information()
        
        # Extract risk factors
        extracted_data['risk_factors'] = extractor.extract_risk_factors()
        
    finally:
        extractor.close()
        
    return extracted_data

class OpenOfferExtractor:
    def __init__(self, pdf_path: str):
        """Initialize with PDF path."""
        self.pdf = pdfplumber.open(pdf_path)
        self.toc_data = self._extract_toc()

        #for key in self.toc_data.keys():
        #    print(f"ToC Item:{key} \n Data:{self.toc_data[key]}")
        
    def _extract_toc(self) -> Dict[str, int]:
        """
        Extract TOC with section names.
        Returns dict with section names as keys and page numbers as values.
        """
        toc_pattern = r'(?:\d+\.)?\s*(.*?)\.{2,}\s*(\d+)$'
        toc_mapping = {}
        
        # Find TOC page
        for page_num, page in enumerate(self.pdf.pages[:20]):
            text = page.extract_text()
            if "TABLE OF CONTENTS" in text:
                lines = text.split('\n')
                for line in lines:
                    match = re.search(toc_pattern, line)
                    if match:
                        section_name = match.group(1).strip()
                        page_num = int(match.group(2))
                        toc_mapping[section_name] = page_num
                        #print (f"Section:{section_name} --> [{page_num}]")
                break
                
        return toc_mapping
    
    def extract_section_content(self, section_name: str) -> str:
        """
        Extract content from a specific section.
        Args:
            section_name: Name of the section to extract
        Returns:
            Extracted text content
        """
        if section_name not in self.toc_data:
            raise ValueError(f"Section '{section_name}' not found in TOC")
            
        start_page = self.toc_data[section_name]
        content = []
        
        # Convert to 0-based index
        current_page = start_page - 1
        
        while current_page < len(self.pdf.pages):
            page = self.pdf.pages[current_page]
            text = page.extract_text()
            
            # Check if we've reached the next section
            next_section_found = False
            for next_section, next_page in self.toc_data.items():
                if next_page > start_page and next_section in text:
                    next_section_found = True
                    break
                    
            if next_section_found and current_page > start_page - 1:
                break
                
            # Extract tables from the page
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    content.append("\nTABLE:")
                    content.extend(" | ".join(str(cell) for cell in row) for row in table)
                    content.append("\n")
            
            content.append(text)
            current_page += 1
            
        return "\n".join(content)
    
    def get_section_names(self) -> List[str]:
        """Return list of all available section names."""
        return list(self.toc_data.keys())
    
    def extract_all_sections(self) -> Dict[str, str]:
        """Extract content from all sections."""
        return {name: self.extract_section_content(name) for name in self.toc_data.keys()}
    
    def extract_forms(self) -> Dict[str, str]:
        """Extract specifically the forms sections."""
        forms = {}
        for name in self.toc_data.keys():
            if "FORM" in name.upper():
                forms[name] = self.extract_section_content(name)
        return forms
    
    def close(self):
        """Close the PDF file."""
        self.pdf.close()

def extract_open_offer_data(pdf_path: str, section_names: List[str] = None) -> Dict[str, str]:
    """
    Main function to extract data from TOC sections.
    Args:
        pdf_path: Path to the PDF file
        section_names: List of section names to extract (optional)
    Returns:
        Dictionary containing extracted data
    """
    extractor = OpenOfferExtractor(pdf_path)
    
    try:
        # Print available sections for reference
        print("Available sections:")
        for name in extractor.get_section_names():
            print(f"- {name}")
            
        if section_names:
            # Validate section names
            invalid_sections = [name for name in section_names if name not in extractor.get_section_names()]
            if invalid_sections:
                raise ValueError(f"Invalid section names: {invalid_sections}")
                
            return {name: extractor.extract_section_content(name) for name in section_names}
        else:
            # Extract all sections if none specified
            return extractor.extract_all_sections()
            
    finally:
        extractor.close()

# Example usage:


def rhp_extractor_example():
    #sections = [
    #"SECTION II - ISSUE DOCUMENT SUMMARY",
    #"OBJECTS OF THE ISSUE",
    #"INDUSTRY OVERVIEW"
    #]"SECTION V - ABOUT THE COMPANY"
    sections = [
    "ABOUT THE COMPANY"
    ]


    data = extract_rhp_data("karni_rhp.pdf", sections)

    for section in sections:
        for key in data:
            if section in key:
                print("===============================")
                print(f"Section: {section}")
                print(data[key]['text'])
                #print(data[key]['tables'])
                print("===============================")


    print(data)

def open_offer_extractor_example():
    # Extract specific sections by name
    sections_needed = [
    'DETAILS OF THIS OFFER',
    'BACKGROUND OF ACQUIRER',
    'BACKGROUND OF THE TARGET COMPANY',
    'OFFER PRICE AND FINANCIAL ARRANGEMENTS'
    ]
    data = extract_open_offer_data("of1.pdf", sections_needed)

    for key in data:
        print(f"===========section:{key}\n{data[key]}\n===============\n")
    #print(f"Section data:{data}")

    # Or extract all sections
    #all_data = extract_open_offer_data("of1.pdf")

def main():
    #rhp_extractor_example()
    open_offer_extractor_example()


if __name__ == '__main__':
    main()