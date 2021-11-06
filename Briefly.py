import streamlit as st                      #Web App
from gnewsclient import gnewsclient         # for fetching google news
from newspaper import Article               # to obtain text from news articles
import spacy                                # to obtain keyword
from annotated_text import annotated_text   # to display keywords
import requests                             


# Load sshleifer/distilbart-cnn-12-6 model using Accelerated Inference API
API_URL = "https://api-inference.huggingface.co/models/sshleifer/distilbart-cnn-12-6"



def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()


data = gnewsclient.NewsClient(max_results=0) 

st.cache(allow_output_mutation=True)
# obtain urls and it's content
def getNews(topic,location):                
    count=0
    contents=[]
    titles=[]
    authors=[]
    urls=[]
    data = gnewsclient.NewsClient(language='english',location=location,topic=topic,max_results=10) 
    news = data.get_news()  
    for item in news:
        url=item['link']
        article = Article(url)
        try:
            article.download()
            article.parse()
            temp=item['title'][::-1]
            index=temp.find("-")
            temp=temp[:index-1][::-1]
            urls.append(url)
            contents.append(article.text)
            titles.append(item['title'][:-index-1])    
            authors.append(temp)
            count+=1
            if(count==5):
                break
        except:
            continue 
    return contents,titles,authors,urls 

 
 # Summarizes the content- minimum word limit 30 and maximum 60
def getNewsSummary(contents):   
    summaries=[]     
    for content in contents:
        summary = query({"inputs":content})[0]["summary_text"]
        summaries.append(summary) 
    return summaries


# Obtain 4 keywords from content (person,organisation or geopolitical entity)
def generateKeyword(contents):            
    keywords=[]
    words=[]
    nlp = spacy.load("en_core_web_lg")    
    labels=["PERSON","ORG","GPE"]
    for content in contents:
        doc=nlp(content)
        keys=[]
        limit=0
        for ent in doc.ents:
            key=ent.text.upper()
            label=ent.label_
            if(key not in words and key not in keywords and label in labels): 
                keys.append(key)
                limit+=1
                for element in key.split():
                    words.append(element)
            if(limit==4):
                keywords.append(keys)
                break                           
    return keywords


# Display title,author and summary in streamlit
def DisplaySummary(titles,authors,summaries,keywords,urls):
    for i in range(5):
        if(i+1<=len(summaries) and i+1<=len(keywords)):
            st.text("")
            st.subheader(f'[{titles[i]}] ({urls[i]})')
            st.markdown(f'<b>{authors[i]}</b>',unsafe_allow_html=True)
            st.write(summaries[i])
            if(len(keywords[i])==4):
                annotated_text("KEYWORDS :",(keywords[i][0],"","#faa")," ",(keywords[i][1],"","#faa")," ",(keywords[i][2],"","#faa")," ",(keywords[i][3],"","#faa"))
            elif(len(keywords[i])==3):
                annotated_text("KEYWORDS :",(keywords[i][0],"","#faa")," ",(keywords[i][1],"","#faa")," ",(keywords[i][2],"","#faa"))  
            elif(len(keywords[i])==2):
                annotated_text("KEYWORDS :",(keywords[i][0],"","#faa")," ",(keywords[i][1],"","#faa"))  
            elif(len(keywords[i])==1):
                annotated_text("KEYWORDS :",(keywords[i][0],"","#faa"))            
        st.text("")
        st.text("")


def main():               
    st.title('Briefly')
    with st.expander('Read trending news in less than 60 words...', expanded=True):
        with st.form(key='form1'):
            topic=st.selectbox('Category:',data.topics[2:]+["World"])
            location=st.selectbox('Location:',data.locations)        
            submit_button=st.form_submit_button() 
                          
    if submit_button:
        with st.spinner('Fetching news...'):            
            contents,titles,authors,urls=getNews(topic,location)
            summaries=getNewsSummary(contents)          
            keywords=generateKeyword(contents)
        DisplaySummary(titles,authors,summaries,keywords,urls)


if __name__ == '__main__':
    main()
