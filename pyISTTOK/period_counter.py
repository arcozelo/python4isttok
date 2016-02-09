import numpy

def period_counter(input_data, threshold, tester = numpy.append(numpy.ones(100),numpy.zeros(1))):
    count = 0
    #tester = numpy.append(numpy.ones(200),numpy.zeros(1));

    mask = input_data > threshold;

    for i in range(len(mask[250:])-len(tester)):
        if numpy.sum(numpy.equal(mask[250+i:250+i+len(tester)],tester))==len(tester):
	    count+=1

    return count;
