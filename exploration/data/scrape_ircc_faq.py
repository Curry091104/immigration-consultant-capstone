import requests
from bs4 import BeautifulSoup
import json
import os

def scrape_ircc_faqs():
    base_url = "https://www.canada.ca"
    # Studey permit and PGWP Sections
    sections = [
        # Study Permit Section
        "/en/immigration-refugees-citizenship/services/study-canada/study-permit/eligibility.html",
        "/en/immigration-refugees-citizenship/services/study-canada/study-permit/get-documents.html",
        "/en/immigration-refugees-citizenship/services/study-canada/study-permit/apply.html",
        "/en/immigration-refugees-citizenship/services/study-canada/study-permit/after-apply-next-steps.html",
        "/en/immigration-refugees-citizenship/services/study-canada/study-permit/prepare-arrival.html",
        "/en/immigration-refugees-citizenship/services/study-canada/study-permit/while-studying.html",
        
        # PGWP Section
        "/en/immigration-refugees-citizenship/services/study-canada/work/after-graduation.html",
        "/en/immigration-refugees-citizenship/services/study-canada/work/after-graduation/eligibility.html",
        "/en/immigration-refugees-citizenship/services/study-canada/work/after-graduation/apply.html",
        
        # Work while studying Section
        "/en/immigration-refugees-citizenship/services/study-canada/work.html",
        "/en/immigration-refugees-citizenship/services/study-canada/work/work-on-campus.html",
        "/en/immigration-refugees-citizenship/services/study-canada/work/work-off-campus.html",
        
        # Stay after graduation Section
        "/en/immigration-refugees-citizenship/services/study-canada/extend-study-permit.html",
        "/en/immigration-refugees-citizenship/services/study-canada/study-permit/extend.html"
    ]
    
    faqs = []
    faq_id = 1

    for section_url in sections:
        print(f"Scraping {section_url}...")
        
        try:
            response = requests.get(base_url + section_url)
            soup = BeautifulSoup(response.text, 'html.parser')

            if "work/after-graduation" in section_url:
                section_tag = "pgwp"
            elif "work" in section_url:
                section_tag = "work while studying"
            else:
                section_tag = "study permit"

            section_name = soup.find('h1').text.strip()

            details = soup.find_all(['details', 'h2', 'h3', 'h4'])
            
            for detail in details:
                if detail.name == 'details':
                    question = detail.find('summary').text.strip()
                    answer_div = detail.find(['div', 'p'])
                    answer = answer_div.text.strip() if answer_div else ""
                    links = []
                    
                   
                    for i, a in enumerate(detail.find_all('a', href=True)):
                        href = a['href']
                        if not href.startswith('http'):
                            href = base_url + href
                        links.append(f"link{i+1}: {href}")
                    
                    faq = {
                        "faq_id": f"faq_{faq_id}",
                        "tags": [section_tag, section_name.lower()],
                        "question": question,
                        "answer": answer,
                        "hyperlinks": links
                    }
                    
                    faqs.append(faq)
                    faq_id += 1
                    print(f"Added FAQ: {question[:50]}...")
                
        except Exception as e:
            print(f"Error scraping {section_url}: {str(e)}")
    
    output_file = 'ircc_faqs.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(faqs, f, indent=4, ensure_ascii=False)
    
    print(f"\nSaved {len(faqs)} FAQs to {output_file}")

if __name__ == "__main__":
    scrape_ircc_faqs()