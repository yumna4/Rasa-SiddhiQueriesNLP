from rasa_nlu.converters import load_data
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.model import Trainer
import nltk
from query import QueryGenerator
queryGenerator=QueryGenerator()

class Siddhi:
    def prepareForNLP(self,text):
        sentences = nltk.sent_tokenize(text)
        sentences = [nltk.word_tokenize(sent) for sent in sentences]
        sentences = [nltk.pos_tag(sent) for sent in sentences]
        return sentences

    def chunk(self,sentence):
        #GREATER THAN 4, THE LAST 4 EVENTS, THE AVERAGE TEMPERATURE, PER SENSOR
        #5:THAT ARE /is above/below 59
        #6:netween 5 and 4
        #7:WITIN A 10 MINUTES WINDOW
        chunkToExtract = """
        NP: {<NN|NNS|NNP><WDT>?<VBZ|VBP>?<JJR><IN><CD|NNS>}
            {<NNS|NN><IN><CD>}
            {<DT>?<JJ><CD><NNS|NN>}
            {<JJ|JJS><NN|NNS>}
            {<WDT><VBP|VBZ><IN><CD>}
            {<IN><CD><CC><CD>}
            {<CD><NN|NNS><RB|VBP>}
            {<JJ|JJS><NN|NNS>(<IN><NN|NNS>)?}
            {<NN>?<IN><DT>?<NN|NNS>}"""
        parser = nltk.RegexpParser(chunkToExtract)
        result = parser.parse(sentence)

        chunks=[]
        for subtree in result.subtrees():
            if subtree.label() == 'NP':
                t = subtree
                t = ' '.join(word for word, pos in t.leaves())
                chunks.append(t)
        return chunks

    #for filter in training file, put greater than 4, a value, even for group by and aggregate
    def getSiddhiQuery(self,NLQuery):
        sentences = self.prepareForNLP(NLQuery)

        for sentence in sentences:

            chunks=self.chunk(sentence)

        training_data = load_data('data/examples/rasa/intents.json')
        trainer = Trainer(RasaNLUConfig("sample_configs/config_siddhi.json"))
        trainer.train(training_data)
        model_directory = trainer.persist('./projects/default/')  # Returns the directory the model is stored in

        from rasa_nlu.model import Metadata, Interpreter
        # where `model_directory points to the folder the model is persisted in
        interpreter = Interpreter.load(model_directory, RasaNLUConfig("sample_configs/config_spacy.json"))





        training_data1 = load_data('data/examples/rasa/display.json')
        trainer1 = Trainer(RasaNLUConfig("sample_configs/config_display.json"))
        trainer1.train(training_data1)
        model_directory1 = trainer1.persist('./projects/default/')  # Returns the directory the model is stored in
        interpreter1 = Interpreter.load(model_directory1, RasaNLUConfig("sample_configs/config_spacy.json"))
        a1=(interpreter1.parse(NLQuery))



        values=[]
        for chunk in chunks:


            a=(interpreter.parse(chunk))

            if a['intent']['confidence']>0.6:
                # print (chunk)
                # print (a)
                intent=a['intent']['name']
                # print (intent)
                ent={}
                entities=a['entities']
                for entity in entities:
                    ent[entity['entity']]=entity['value']
                if intent=='filter':
                    ent['text']=chunk
                if intent=='aggregate':
                    ent['aggregateAttribute']=chunk.split()[0]
                values.append([intent,ent])

        intents=[value[0] for value in values]
        if 'aggregate' not in intents:
            display=a1['entities'][0]['value']
        else:
            display=""
        # print(intents)
        query=queryGenerator.generateQuery(values,'TempStream',display)

        return (intents,query)



# s=Siddhi()
# print (s.getSiddhiQuery("Show the deviceID and the average temperature per room for the last 10 minutes"))