import numpy as np


class dataAnalyzer(): 
    def __init__(self): 
        ...

    def analyze_weight(self, theWeight): 
        theResponse = ""; 
        theDays = [1, 2, 3, 4, 5, 6, 7]; 
        m, b = np.polyfit(theDays, theWeight, 1); 

        if(m < -2): 
            theResponse = "Weight loss in the past week is too steep. Please refer to a doctor. "; 

        if(m > 2): 
            theResponse = "Weight gain in the past week is too steep. Please refer to a doctor. "; 

        else:
            theResponse = "Weight trends are normal. "; 

        return theResponse; 


    def analyze_avgHR(self, theHR): 
        theResponse = ""; 
        theDays = [1, 2, 3, 4, 5, 6, 7]; 
        m, b = np.polyfit(theDays, theHR, 1); 

        if(m < -5): 
            theResponse = "Heart rate decreased overall in the past week. Cardiovascular health is getting better. "; 

        if(m > 5): 
            theResponse = "Heart rate increase in the past week is too steep. Please refer to a doctor. "; 

        else:
            theResponse = "Heart rate trends are normal. "; 

        return theResponse; 


    def analyze_avgSpO2(self, avgSpO2):
        theResponse = ""; 
        theThreshold = 94; 
        lowValues = [x for x in avgSpO2 if x <= theThreshold]; 

        if(len(lowValues) > 4): 
            theResponse = "Oxygen levels are too low in the past week. Please refer to a doctor. "; 

        else:
            theResponse = "Oxygen levels are normal. "; 

        return theResponse; 


    def analyze_blood_pressure(self, bpS, bpD):
        theResponse = ""; 
        theThreshold_bpS = 130; 
        theThreshold_bpD = 80; 
        unhealthyCount = 0; 

        for i in range(7): 
            if(bpS[i] > theThreshold_bpS and bpD[i] > theThreshold_bpD): 
                unhealthyCount += 1; 

        if(unhealthyCount >= 4): 
            theResponse = "Blood pressure levels are abnormal in the past week. Please refer to a doctor. "; 

        else:
            theResponse = "Blood pressure levels are normal. "; 

        return theResponse; 


