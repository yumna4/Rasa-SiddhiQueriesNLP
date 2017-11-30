from testQueries import TestQueries
tq=TestQueries()
from Siddhi import Siddhi
siddhi=Siddhi()
import time
from sklearn.metrics import accuracy_score
class Main:
    # isTest=raw_input("Is this a Test? (Y/n)>")
    isTest="Y"
    if isTest=="Y":
        startTime=time.time()
        streamName="TempStream"
        queries=tq.getQueries()
        predictions=[]
        fval=[]
        gval=[]
        aval=[]
        wval=[]
        i=1
        for query in queries:
            print ("")
            print (query)

            values=[0,0,0,0]
            try:
                intents,query =siddhi.getSiddhiQuery(query)
                print (query)
                values=[-1,-1,-1,-1]
                if 'filter' in intents:
                    values[0]=1
                if 'aggregate' in intents:
                    values[1]=1
                if 'window' in intents:
                    values[2]=1
                if 'groupBy' in intents:
                    values[3]=1




            except:
                print ("error")

            # intents,query =siddhi.getSiddhiQuery(query)
            # print (query)
            # values=[-1,-1,-1,-1]
            # if 'filter' in intents:
            #     values[0]=1
            # if 'aggregate' in intents:
            #     values[1]=1
            # if 'window' in intents:
            #     values[2]=1
            # if 'groupBy' in intents:
            #     values[3]=1

            for value in values:
                predictions.append(value)
                fval.append(values[0])
                aval.append(values[1])
                wval.append(values[2])
                gval.append(values[3])
            i+=1
        individuals=tq.getIndividuals()
        # print individuals[0]
        actual=tq.getValues()
        print (accuracy_score(predictions,actual))

        # print ("filter",accuracy_score(fval,individuals[0]))
        # print ("aggrigate", accuracy_score(aval,individuals[1]))

        # print ("window",accuracy_score(wval,individuals[2]))
        # print ("group",accuracy_score(gval,individuals[3]))


        # # siddhiQuery=Q.generateQuery("Show the roomNo which have a temperature higher than 20 degrees",["filter"],streamName,Attributes)
        # # print siddhiQuery
        # # actualqueries=tq.getSiddhiQueries()
        # i=0
        # j=["filter",'aggregate','window','group']
        # siddhiQueries=[]
        # for q in range (24):
        #     query=queries[q]
        #     val=actual[4*i:4*i+4]
        #     intents=[j[k] for k in range (4) if val[k]==1]
        #
        #     siddhiQuery=Q.generateQuery(query,intents,streamName,Attributes)
        #     # if siddhiQuery!=actualqueries[q]:
        #     #     # print intents
        #     #     print query
        #     #     print siddhiQuery
        #     #     print actualqueries[q]
        #     #     print ""
        #     #     print ""
        #     siddhiQueries.append(siddhiQuery)
        #     i+=1
        # # #
        # # print "accuracy of final query",accuracy_score(siddhiQueries,actualqueries)
        print (time.time()-startTime)
    if isTest=="n":



        streamName="TempStream"

        nLQuery=input("Natural Language Query>") #input given by user
        while len(nLQuery)>0:


            intents,siddhiQuery=siddhi.getSiddhiQuery(nLQuery)
            print (siddhiQuery)
            nLQuery=input("Natural Language Query>")




