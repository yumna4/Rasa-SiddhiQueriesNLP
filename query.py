# from pycorenlp import StanfordCoreNLP
import pickle
from FilterConditionBuilder import FilterFinder

# nlp = StanfordCoreNLP('http://localhost:9000')

# ASSUMPTION: ATTRIBUTE NAMES SHOULD BE ONE WORD AND NO TMULTIPLE WORDS
#assumption: cannot use temperature values. instead just temperatures



class QueryGenerator:
    def generateQuery(self,values,stream,display):

        sampleQuery="from <inputStreamName> [<filterCondition>]#window.<window name>(<windowParameters>) select aggregateWord(<attributes>) as <newAttribute> <attributeNames> group by <groupAttribute> having <havingCondition>"
        sampleQuery=sampleQuery.replace("<inputStreamName>",stream)


        intents=[value[0] for value in values]
        for value in values:
            intent=value[0]
            entities=value[1]

            if intent == "window":

                number=entities['number']
                unit=entities['unit']

                if unit == 'events':
                    expression=number
                    windowType='length'
                else:
                    windowType='time'
                    expression=str(number)+" "+unit

                sampleQuery=sampleQuery.replace("<window name>",windowType)
                sampleQuery=sampleQuery.replace("<windowParameters>",expression)



            elif intent == "groupBy":
                try:
                    groupAttribute=entities['attribute']
                    sampleQuery=sampleQuery.replace("<groupAttribute>",groupAttribute)
                except:
                    intents.remove('groupBy')



            # cannot handle when user says coolest room or warmest room
            if intent == "aggregate":
                # try:

                word=entities['aggregator']
                if word in ["maximum","highest","highest","greatest","most"]:
                    aggregateWord="max"
                elif word in ["minimum","lowest","smallest","least"]:
                    aggregateWord='min'
                elif word in ["average"]:
                    aggregateWord="avg"
                elif word in ["total","sum","summation"]:
                    aggregateWord="sum"
                elif word in ["count"]:
                    aggregateWord="count"


                # this part can be improved and simplified via dependency parsing, this may be wrong when like :
                # show roomno when temp is maximum in last 10 minutes
                # remove this when intent detection accuracy is better
                aggregateAttribute=entities['aggregateAttribute']
                newAttribute=aggregateWord+aggregateAttribute
                sampleQuery=sampleQuery.replace("<newAttribute>",newAttribute)
                aggregateExpression=aggregateWord+"("+aggregateAttribute+")"
                sampleQuery=sampleQuery.replace("aggregateWord(<attributes>)",aggregateExpression)
                sampleQuery=sampleQuery.replace(" <attributeNames>","")

                # except:
                #     intents.remove('aggregate')



            # assumption: no filters along with having
            # if filter with grouo then filter is having, if filter with aggregate then filter is having
            elif intent == "filter":
                number=entities['amount']
                filterAttribute=entities['filterAttribute']
                ff=FilterFinder()
                model=pickle.load(open('findfilter_model.sav', 'rb'))
                prepared=ff.prepare(entities['text'])
                function=model.predict([prepared])
                index=int(function)
                filterTypes=[">","<","="," between "]
                function=filterTypes[index-1]

                filterCondition=filterAttribute+function+number


                if "group" in intents or "aggregate" in intents:
                    if "aggregate" in intents:
                        sampleQuery=sampleQuery.replace("<havingCondition>",filterCondition)
                        sampleQuery=sampleQuery.replace(" [<filterCondition>]","")
                    else:
                        sampleQuery=sampleQuery.replace("<havingCondition>",filterCondition)
                        sampleQuery=sampleQuery.replace(" [<filterCondition>]","")
                else:
                    sampleQuery=sampleQuery.replace("<filterCondition>",filterCondition)
                    sampleQuery=sampleQuery.replace("having <havingCondition>","")

        if "window" not in intents:
            sampleQuery=sampleQuery.replace("#window.<window name>(<windowParameters>)","")
        if "groupBy" not in intents:
            sampleQuery=sampleQuery.replace("group by <groupAttribute>","")

        if "aggregate" not in intents:

            sampleQuery=sampleQuery.replace("aggregateWord(<attributes>) as <newAttribute>","")


        if "filter" not in intents:

            sampleQuery=sampleQuery.replace(" [<filterCondition>]","")
            sampleQuery=sampleQuery.replace("having <havingCondition>","")

        sampleQuery=sampleQuery.replace(" <attributeNames>",display)
        return sampleQuery

