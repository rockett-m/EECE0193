//Copyright (c) 2017-2019, IIT Hyderabad. See LICENSE file in the top-level directory
//Copyright (c) 2015-2016, UT-Battelle, LLC. See LICENSE file in the top-level directory
// This file contains code from NVSim, (c) 2012-2013,  Pennsylvania State University 
//and Hewlett-Packard Company. See LICENSE_NVSim file in the top-level directory.
//No part of DESTINY Project, including this file, may be copied,
//modified, propagated, or distributed except according to the terms
//contained in the LICENSE file.


#include "Mat.h"
#include "formula.h"
#include "global.h"

Mat::Mat() {
	// TODO Auto-generated constructor stub
	initialized = false;
	invalid = false;
}

Mat::~Mat() {
	// TODO Auto-generated destructor stub
}

void Mat::Initialize(int _numRowSubarray, int _numColumnSubarray, int _numAddressBit, long _numDataBit,
		int _numWay, int _numRowPerSet, bool _split, int _numActiveSubarrayPerRow, int _numActiveSubarrayPerColumn,
		int _muxSenseAmp, bool _internalSenseAmp, int _muxOutputLev1, int _muxOutputLev2,
		BufferDesignTarget _areaOptimizationLevel, MemoryType _memoryType, int _stackedDieCount,
        int _partitionGranularity, int monolithicStackCount) {
	if (initialized)
		cout << "[Mat] Warning: Already initialized!" << endl;

	numRowSubarray = _numRowSubarray;
	numColumnSubarray = _numColumnSubarray;
	numAddressBit = _numAddressBit;
	numDataBit = _numDataBit;
	numWay = _numWay;
	numRowPerSet = _numRowPerSet;
	split = _split;
	internalSenseAmp = _internalSenseAmp;
	areaOptimizationLevel = _areaOptimizationLevel;
	memoryType =_memoryType;
    stackedDieCount = _stackedDieCount;
    partitionGranularity = _partitionGranularity;

	if (_numActiveSubarrayPerRow > numColumnSubarray) {
		cout << "[Mat] Warning: The number of active subarray per row is larger than the number of subarray per row!"  << endl;
		cout << _numActiveSubarrayPerRow << " > " << numColumnSubarray << endl;
		numActiveSubarrayPerRow = numColumnSubarray;
	} else {
		numActiveSubarrayPerRow = _numActiveSubarrayPerRow;
	}
	if (_numActiveSubarrayPerColumn > numRowSubarray) {
		cout << "[Mat] Warning: The number of active subarray per column is larger than the number of subarray per column!"  << endl;
		cout << _numActiveSubarrayPerColumn << " > " << numRowSubarray << endl;
		numActiveSubarrayPerColumn = numRowSubarray;
	} else {
		numActiveSubarrayPerColumn = _numActiveSubarrayPerColumn;
	}
	muxSenseAmp = _muxSenseAmp;
	muxOutputLev1 = _muxOutputLev1;
	muxOutputLev2 = _muxOutputLev2;

	long long numRow = 0;		/* Number of rows in a subarray */
	long long numColumn = 0;	/* Number of columns in a subarray */

	/* The number of address bits that are used to power gate inactive subarrays */
	int numAddressForGating = (int)(log2(numRowSubarray * numColumnSubarray / numActiveSubarrayPerColumn / numActiveSubarrayPerRow)+0.1);
	_numAddressBit -= numAddressForGating;	/* Only use the effective address bits in the following calculation */
	if (_numAddressBit <= 0) {
		/* too aggressive partitioning */
		invalid = true;
		initialized = true;
		return;
	}

	/* Determine the number of rows in a subarray */
	numRow = 1 << _numAddressBit;
	if (memoryType == data)
		numRow *= numWay;	/* Only for cache design that partitions a set into multiple rows */
	numRow /= (muxSenseAmp * muxOutputLev1 * muxOutputLev2);	/* Distribute to column decoding */
	if (numRow == 0) {
		invalid = true;
		initialized = true;
		return;
	}

	numColumn = (long long)numDataBit / (numActiveSubarrayPerRow * numActiveSubarrayPerColumn);	/* Adjust the number of columns depending on the access types */
	if (numColumn == 0) {
		invalid = true;
		initialized = true;
		return;
	}

	numColumn *= muxSenseAmp * muxOutputLev1 * muxOutputLev2;
	if (memoryType == tag)
		numColumn *= numWay;

	subarray.Initialize(numRow, numColumn, numRowPerSet > 1, true /* TO-DO: need to correct */,
			muxSenseAmp, internalSenseAmp, muxOutputLev1, muxOutputLev2, areaOptimizationLevel, monolithicStackCount);

	if (subarray.invalid) {
		invalid = true;
		initialized = true;
		return;
	}
	subarray.CalculateArea();	/* the area needs to be calculated during the initialization because the size dimension needs to be called by others */

	int numAddressRowPredecoderBlock1 = _numAddressBit - (int)(log2(muxSenseAmp * muxOutputLev1 * muxOutputLev2)+0.1);	/* The address bit on row decodeing */
	if (numAddressRowPredecoderBlock1 < 0) {
		invalid = true;
		initialized = true;
		return;
	}
	int numAddressRowPredecoderBlock2 = 0;
	if (numAddressRowPredecoderBlock1 > 3) {	/* Block 2 is needed */
		numAddressRowPredecoderBlock2 = numAddressRowPredecoderBlock1 / 2;
		numAddressRowPredecoderBlock1 = numAddressRowPredecoderBlock1 - numAddressRowPredecoderBlock2;
	}

    totalPredecoderOutputBits = 1 << numAddressRowPredecoderBlock1; 
    totalPredecoderOutputBits += 1 << numAddressRowPredecoderBlock2; 

	double capLoadRowPredecoder = subarray.height * localWire->capWirePerUnit * numRowSubarray / 2
			+ subarray.width * localWire->capWirePerUnit * numColumnSubarray / 2;	/* Assume the predecoder is at the center */
	rowPredecoderBlock1.Initialize(numAddressRowPredecoderBlock1, capLoadRowPredecoder, 0 /* TO-DO */);
	rowPredecoderBlock2.Initialize(numAddressRowPredecoderBlock2, capLoadRowPredecoder, 0 /* TO-DO */);

	double capLoadMuxPredecoder = MAX(0, subarray.height * localWire->capWirePerUnit * (numRowSubarray - 2) / 2)
			+ MAX(0, subarray.width * localWire->capWirePerUnit * (numColumnSubarray - 2) / 2);
	int numAddressBitlineMuxPredecoderBlock1 = (int)(log2(muxSenseAmp) + 0.1);
	int numAddressBitlineMuxPredecoderBlock2 = 0;
	if (numAddressBitlineMuxPredecoderBlock1 > 3) {		/* Block 2 is needed */
		numAddressBitlineMuxPredecoderBlock2 = numAddressBitlineMuxPredecoderBlock1 / 2;
		numAddressBitlineMuxPredecoderBlock1 = numAddressBitlineMuxPredecoderBlock1 - numAddressBitlineMuxPredecoderBlock2;
	}
	bitlineMuxPredecoderBlock1.Initialize(numAddressBitlineMuxPredecoderBlock1, capLoadMuxPredecoder, 0 /* TO-DO */);
	bitlineMuxPredecoderBlock2.Initialize(numAddressBitlineMuxPredecoderBlock2, capLoadMuxPredecoder, 0 /* TO-DO */);

    totalPredecoderOutputBits += 1 << numAddressBitlineMuxPredecoderBlock1; 
    totalPredecoderOutputBits += 1 << numAddressBitlineMuxPredecoderBlock2; 

	int numAddressSenseAmpMuxLev1PredecoderBlock1 = (int)(log2(muxOutputLev1) + 0.1);
	int numAddressSenseAmpMuxLev1PredecoderBlock2 = 0;
	if (numAddressSenseAmpMuxLev1PredecoderBlock1 > 3) { /* Block 2 is needed */
		numAddressSenseAmpMuxLev1PredecoderBlock2 = numAddressSenseAmpMuxLev1PredecoderBlock1 / 2;
		numAddressSenseAmpMuxLev1PredecoderBlock1 = numAddressSenseAmpMuxLev1PredecoderBlock1 - numAddressSenseAmpMuxLev1PredecoderBlock2;
	}
	senseAmpMuxLev1PredecoderBlock1.Initialize(numAddressSenseAmpMuxLev1PredecoderBlock1, capLoadMuxPredecoder, 0 /* TO-DO */);
	senseAmpMuxLev1PredecoderBlock2.Initialize(numAddressSenseAmpMuxLev1PredecoderBlock2, capLoadMuxPredecoder, 0 /* TO-DO */);

    totalPredecoderOutputBits += 1 << numAddressSenseAmpMuxLev1PredecoderBlock1; 
    totalPredecoderOutputBits += 1 << numAddressSenseAmpMuxLev1PredecoderBlock2; 

	int numAddressSenseAmpMuxLev2PredecoderBlock1 = (int)(log2(muxOutputLev2) + 0.1);
	int numAddressSenseAmpMuxLev2PredecoderBlock2 = 0;
	if (numAddressSenseAmpMuxLev2PredecoderBlock1 > 3) { /* Block 2 is needed */
		numAddressSenseAmpMuxLev2PredecoderBlock2 = numAddressSenseAmpMuxLev2PredecoderBlock1 / 2;
		numAddressSenseAmpMuxLev2PredecoderBlock1 = numAddressSenseAmpMuxLev2PredecoderBlock1 - numAddressSenseAmpMuxLev2PredecoderBlock2;
	}
	senseAmpMuxLev2PredecoderBlock1.Initialize(numAddressSenseAmpMuxLev2PredecoderBlock1, capLoadMuxPredecoder, 0 /* TO-DO */);
	senseAmpMuxLev2PredecoderBlock2.Initialize(numAddressSenseAmpMuxLev2PredecoderBlock2, capLoadMuxPredecoder, 0 /* TO-DO */);

    totalPredecoderOutputBits += 1 << numAddressSenseAmpMuxLev2PredecoderBlock1; 
    totalPredecoderOutputBits += 1 << numAddressSenseAmpMuxLev2PredecoderBlock2; 

	if (memoryType == tag && internalSenseAmp) {
		comparator.Initialize(numDataBit, 0 /*TO-DO: need to fix */);
	}

    /* Initialize TSV connections. */
    if (stackedDieCount > 1 && partitionGranularity != 0) {
        TSV_type tsv_type = tech->WireTypeToTSVType(inputParameter->maxLocalWireType);
        tsvArray.Initialize(tsv_type);
    }

	initialized = true;
}

void Mat::CalculateArea() {
	if (!initialized) {
		cout << "[Mat] Error: Require initialization first!" << endl;
	} else if (invalid) {
		height = width = area = invalid_value;
	} else {
		/* subarray CalculateArea() is already called during the initialization */
		rowPredecoderBlock1.CalculateArea();
		rowPredecoderBlock2.CalculateArea();
		bitlineMuxPredecoderBlock1.CalculateArea();
		bitlineMuxPredecoderBlock2.CalculateArea();
		senseAmpMuxLev1PredecoderBlock1.CalculateArea();
		senseAmpMuxLev1PredecoderBlock2.CalculateArea();
		senseAmpMuxLev2PredecoderBlock1.CalculateArea();
		senseAmpMuxLev2PredecoderBlock2.CalculateArea();

		double areaAllPredecoderBlocks = rowPredecoderBlock1.area + rowPredecoderBlock2.area
				+ bitlineMuxPredecoderBlock1.area + bitlineMuxPredecoderBlock2.area
				+ senseAmpMuxLev1PredecoderBlock1.area + senseAmpMuxLev1PredecoderBlock2.area
				+ senseAmpMuxLev2PredecoderBlock1.area + senseAmpMuxLev2PredecoderBlock2.area;
		width = subarray.width * numColumnSubarray;
		height = subarray.height * numRowSubarray;

        areaAllLogicBlocks = areaAllPredecoderBlocks;

        /* For any partition granularity besides coarse grained, predecoders go on logic layer. */
        if (stackedDieCount > 1 && partitionGranularity == 1) {
            /* Add TSV area for predecoders. */
            tsvArray.CalculateArea();
            double redundancyFactor = inputParameter->tsvRedundancy;
            double areaTSV = tsvArray.area * totalPredecoderOutputBits
                             * redundancyFactor;
            tsvArray.numTotalBits = (int)((double)(totalPredecoderOutputBits * redundancyFactor) + 0.1);
            tsvArray.numAccessBits = tsvArray.numTotalBits;

            /* Area of logic layer is computed during result output. */
            if (width > height)
                width += sqrt(areaTSV);
            else
                height += sqrt(areaTSV);
        } else {
            /* Add the predecoders' area */
            if (width > height)
                width += sqrt(areaAllPredecoderBlocks); // we don't want to have too much white space here.
            else
                height += sqrt(areaAllPredecoderBlocks);
        }

		if (memoryType == tag && internalSenseAmp) {
			comparator.CalculateArea();
            areaAllLogicBlocks += comparator.area;
            // TSVs for comparator are added above in previous conditional
            if (stackedDieCount <= 1 || partitionGranularity != 1) {
                height += numWay * comparator.area / width;
            }
		}

		area = height * width;
	}
}

void Mat::CalculateRC() {
	if (!initialized) {
		cout << "[Mat] Error: Require initialization first!" << endl;
	} else if (!invalid){
		/* subarray does not have CalculateRC() function, since it is integrated as a part of initialization */
		rowPredecoderBlock1.CalculateRC();
		rowPredecoderBlock2.CalculateRC();
		bitlineMuxPredecoderBlock1.CalculateRC();
		bitlineMuxPredecoderBlock2.CalculateRC();
		senseAmpMuxLev1PredecoderBlock1.CalculateRC();
		senseAmpMuxLev1PredecoderBlock2.CalculateRC();
		senseAmpMuxLev2PredecoderBlock1.CalculateRC();
		senseAmpMuxLev2PredecoderBlock2.CalculateRC();
		if (memoryType == tag && internalSenseAmp) {
			comparator.CalculateRC();
		}
	}
}

void Mat::CalculateLatency(double _rampInput) {
	if (!initialized) {
		cout << "[Mat] Error: Require initialization first!" << endl;
	} else if (invalid) {
		readLatency = writeLatency = invalid_value;
	} else {
		/* Calculate the predecoder blocks latency */
		rowPredecoderBlock1.CalculateLatency(_rampInput);
		rowPredecoderBlock2.CalculateLatency(_rampInput);
		bitlineMuxPredecoderBlock1.CalculateLatency(_rampInput);
		bitlineMuxPredecoderBlock2.CalculateLatency(_rampInput);
		senseAmpMuxLev1PredecoderBlock1.CalculateLatency(_rampInput);
		senseAmpMuxLev1PredecoderBlock2.CalculateLatency(_rampInput);
		senseAmpMuxLev2PredecoderBlock1.CalculateLatency(_rampInput);
		senseAmpMuxLev2PredecoderBlock2.CalculateLatency(_rampInput);

		double rowPredecoderLatency = MAX(rowPredecoderBlock1.readLatency, rowPredecoderBlock2.readLatency);
		double bitlineMuxPredecoderLatency = MAX(bitlineMuxPredecoderBlock1.readLatency,
				bitlineMuxPredecoderBlock2.readLatency);
		double senseAmpMuxLev1PredecoderLatency = MAX(senseAmpMuxLev1PredecoderBlock1.readLatency,
				senseAmpMuxLev1PredecoderBlock2.readLatency);
		double senseAmpMuxLev2PredecoderLatency = MAX(senseAmpMuxLev2PredecoderBlock1.readLatency,
				senseAmpMuxLev2PredecoderBlock2.readLatency);
		predecoderLatency = MAX(MAX(rowPredecoderLatency, bitlineMuxPredecoderLatency),
				MAX(senseAmpMuxLev1PredecoderLatency, senseAmpMuxLev2PredecoderLatency));

        if (stackedDieCount > 1 && partitionGranularity != 0) {
            /* Add TSV latency here -- Once for address, once for data. */
            double tsvReadRampInput;
            double tsvWriteRampInput;

            // Normally senseAmpMuxLev2 is the last driver from Mat
            //tsvReadRampInput = mat.subarray.senseAmpMuxLev2.rampOutput;
            tsvReadRampInput = 1e20;

            // Write TSVs should be driven by predecoders -- Use the min for worst case
            tsvWriteRampInput = infinite_ramp; 

            // Add TSV energy ~ Assume outside of bank area
            // Use comparator for tag read ramp input with internal sensing
            tsvArray.CalculateLatencyAndPower(tsvReadRampInput, tsvWriteRampInput); 

            // Address TSV latency
            predecoderLatency += (stackedDieCount-1) * tsvArray.writeLatency;
        }

		/* Caluclate subarray latency */
		subarray.CalculateLatency(MIN(rowPredecoderBlock1.rampOutput, rowPredecoderBlock2.rampOutput));

		/* Add them together */
		readLatency = predecoderLatency + subarray.readLatency;
		writeLatency = predecoderLatency + subarray.writeLatency;
		/* for RESET and SET only */
		resetLatency = predecoderLatency + subarray.resetLatency;
		setLatency = predecoderLatency + subarray.setLatency;
		/* for MLC MRAM only*/
		resetLatencySoft = predecoderLatency + subarray.resetLatencySoft;
		setLatencySoft = predecoderLatency + subarray.setLatencySoft;

        /* Valid for DRAM and eDRAM only. */
        refreshLatency = predecoderLatency + subarray.refreshLatency;
        refreshLatency *= numColumnSubarray; // TOTAL refresh time for all subarrays

        /*valid for DWM only */
        shiftLatency = predecoderLatency + subarray.shiftLatency;

		if (memoryType == tag && internalSenseAmp) {
			comparator.CalculateLatency(_rampInput);
			readLatency += comparator.readLatency;
		}
	}
}

void Mat::CalculatePower() {
	if (!initialized) {
		cout << "[Mat] Error: Require initialization first!" << endl;
	} else if (invalid) {
		readDynamicEnergy = writeDynamicEnergy = leakage = invalid_value;
	} else {
		rowPredecoderBlock1.CalculatePower();
		rowPredecoderBlock2.CalculatePower();
		bitlineMuxPredecoderBlock1.CalculatePower();
		bitlineMuxPredecoderBlock2.CalculatePower();
		senseAmpMuxLev1PredecoderBlock1.CalculatePower();
		senseAmpMuxLev1PredecoderBlock2.CalculatePower();
		senseAmpMuxLev2PredecoderBlock1.CalculatePower();
		senseAmpMuxLev2PredecoderBlock2.CalculatePower();
		subarray.CalculatePower();

		readDynamicEnergy = rowPredecoderBlock1.readDynamicEnergy + rowPredecoderBlock2.readDynamicEnergy
				+ bitlineMuxPredecoderBlock1.readDynamicEnergy + bitlineMuxPredecoderBlock2.readDynamicEnergy
				+ senseAmpMuxLev1PredecoderBlock1.readDynamicEnergy + senseAmpMuxLev1PredecoderBlock2.readDynamicEnergy
				+ senseAmpMuxLev2PredecoderBlock1.readDynamicEnergy + senseAmpMuxLev2PredecoderBlock2.readDynamicEnergy;
		writeDynamicEnergy = rowPredecoderBlock1.writeDynamicEnergy + rowPredecoderBlock2.writeDynamicEnergy
				+ bitlineMuxPredecoderBlock1.writeDynamicEnergy + bitlineMuxPredecoderBlock2.writeDynamicEnergy
				+ senseAmpMuxLev1PredecoderBlock1.writeDynamicEnergy + senseAmpMuxLev1PredecoderBlock2.writeDynamicEnergy
				+ senseAmpMuxLev2PredecoderBlock1.writeDynamicEnergy + senseAmpMuxLev2PredecoderBlock2.writeDynamicEnergy;
        /* Assume the predecoder bits are broadcast, so we don't need to multiply by total subarrays / active. */
        refreshDynamicEnergy = rowPredecoderBlock1.readDynamicEnergy + rowPredecoderBlock2.readDynamicEnergy;
        refreshDynamicEnergy *= subarray.numRow * numRowSubarray; // Total predecoder energy for all REFs
		leakage = rowPredecoderBlock1.leakage + rowPredecoderBlock2.leakage
				+ bitlineMuxPredecoderBlock1.leakage + bitlineMuxPredecoderBlock2.leakage
				+ senseAmpMuxLev1PredecoderBlock1.leakage + senseAmpMuxLev1PredecoderBlock2.leakage
				+ senseAmpMuxLev2PredecoderBlock1.leakage + senseAmpMuxLev2PredecoderBlock2.leakage;
		readDynamicEnergy += subarray.readDynamicEnergy * numActiveSubarrayPerRow * numActiveSubarrayPerColumn;
        /* This is now the total refresh energy for this Mat. */
        refreshDynamicEnergy += subarray.refreshDynamicEnergy * numRowSubarray * numColumnSubarray;
		/* energy consumption on cells */
		cellReadEnergy = subarray.cellReadEnergy * numActiveSubarrayPerRow * numActiveSubarrayPerColumn;
		cellSetEnergy = subarray.cellSetEnergy * numActiveSubarrayPerRow * numActiveSubarrayPerColumn;
		cellResetEnergy = subarray.cellResetEnergy * numActiveSubarrayPerRow * numActiveSubarrayPerColumn;
		cellSetEnergySoft = subarray.cellSetEnergySoft * numActiveSubarrayPerRow * numActiveSubarrayPerColumn;
		cellResetEnergySoft = subarray.cellResetEnergySoft * numActiveSubarrayPerRow * numActiveSubarrayPerColumn;
		/* for RESET and SET only */
		resetDynamicEnergy = writeDynamicEnergy + subarray.resetDynamicEnergy * numActiveSubarrayPerRow * numActiveSubarrayPerColumn;
		setDynamicEnergy = writeDynamicEnergy + subarray.setDynamicEnergy * numActiveSubarrayPerRow * numActiveSubarrayPerColumn;
		resetDynamicEnergySoft = writeDynamicEnergy + subarray.resetDynamicEnergySoft * numActiveSubarrayPerRow * numActiveSubarrayPerColumn;
		setDynamicEnergySoft = writeDynamicEnergy + subarray.setDynamicEnergySoft * numActiveSubarrayPerRow * numActiveSubarrayPerColumn;

		/* total write energy */
		writeDynamicEnergy += subarray.writeDynamicEnergy * numActiveSubarrayPerRow * numActiveSubarrayPerColumn;
		leakage += subarray.leakage * numRowSubarray * numColumnSubarray;

        /*valid for DWM only */
        shiftDynamicEnergy += subarray.shiftDynamicEnergy * numActiveSubarrayPerRow * numActiveSubarrayPerColumn;

        if (stackedDieCount > 1 && partitionGranularity != 0) {
            // Add address TSV energy
            readDynamicEnergy += (stackedDieCount-1) * totalPredecoderOutputBits * tsvArray.readDynamicEnergy;
            writeDynamicEnergy += (stackedDieCount-1) * totalPredecoderOutputBits * tsvArray.writeDynamicEnergy;
            resetDynamicEnergy += (stackedDieCount-1) * totalPredecoderOutputBits * tsvArray.resetDynamicEnergy;
            setDynamicEnergy += (stackedDieCount-1) * totalPredecoderOutputBits * tsvArray.setDynamicEnergy;
            refreshDynamicEnergy += (stackedDieCount-1) * totalPredecoderOutputBits * tsvArray.readDynamicEnergy;

            leakage += tsvArray.numTotalBits * (stackedDieCount-1) * tsvArray.leakage;
        }

		if (memoryType == tag && internalSenseAmp) {
			comparator.CalculatePower();
			readDynamicEnergy += comparator.readDynamicEnergy * numWay;
			writeDynamicEnergy += comparator.writeDynamicEnergy * numWay;
			leakage += comparator.leakage * numWay;
		}

	}
}

void Mat::PrintProperty() {
	cout << "Mat Properties:" << endl;
	FunctionUnit::PrintProperty();
}


Mat & Mat::operator=(const Mat &rhs) {
	height = rhs.height;
	width = rhs.width;
	area = rhs.area;
	readLatency = rhs.readLatency;
	writeLatency = rhs.writeLatency;
    refreshLatency = rhs.refreshLatency;
	readDynamicEnergy = rhs.readDynamicEnergy;
	writeDynamicEnergy = rhs.writeDynamicEnergy;
	resetLatency = rhs.resetLatency;
	setLatency = rhs.setLatency;
	resetLatencySoft = rhs.resetLatencySoft;
	setLatencySoft = rhs.setLatencySoft;
	resetDynamicEnergy = rhs.resetDynamicEnergy;
	setDynamicEnergy = rhs.setDynamicEnergy;
	resetDynamicEnergySoft = rhs.resetDynamicEnergySoft;
	setDynamicEnergySoft = rhs.setDynamicEnergySoft;
	refreshDynamicEnergy = rhs.refreshDynamicEnergy;
	cellReadEnergy = rhs.cellReadEnergy;
	cellSetEnergy = rhs.cellSetEnergy;
	cellResetEnergy = rhs.cellResetEnergy;
	cellSetEnergySoft = rhs.cellSetEnergySoft;
	cellResetEnergySoft = rhs.cellResetEnergySoft;
	leakage = rhs.leakage;
	initialized = rhs.initialized;
	invalid = rhs.invalid;
	numRowSubarray = rhs.numRowSubarray;
	numColumnSubarray = rhs.numColumnSubarray;
	numAddressBit = rhs.numAddressBit;
	numDataBit = rhs.numDataBit;
	numWay = rhs.numWay;
	numRowPerSet = rhs.numRowPerSet;
	split = rhs.split;
	internalSenseAmp = rhs.internalSenseAmp;
	numActiveSubarrayPerRow = rhs.numActiveSubarrayPerRow;
	numActiveSubarrayPerColumn = rhs.numActiveSubarrayPerColumn;
	muxSenseAmp = rhs.muxSenseAmp;
	muxOutputLev1 = rhs.muxOutputLev1;
	muxOutputLev2 = rhs.muxOutputLev2;
	areaOptimizationLevel = rhs.areaOptimizationLevel;
	memoryType = rhs.memoryType;
	predecoderLatency = rhs.predecoderLatency;
    areaAllLogicBlocks = rhs.areaAllLogicBlocks;

	subarray = rhs.subarray;
	rowPredecoderBlock1 = rhs.rowPredecoderBlock1;
	rowPredecoderBlock2 = rhs.rowPredecoderBlock2;
	bitlineMuxPredecoderBlock1 = rhs.bitlineMuxPredecoderBlock1;
	bitlineMuxPredecoderBlock2 = rhs.bitlineMuxPredecoderBlock2;
	senseAmpMuxLev1PredecoderBlock1 = rhs.senseAmpMuxLev1PredecoderBlock1;
	senseAmpMuxLev1PredecoderBlock2 = rhs.senseAmpMuxLev1PredecoderBlock2;
	senseAmpMuxLev2PredecoderBlock1 = rhs.senseAmpMuxLev2PredecoderBlock1;
	senseAmpMuxLev2PredecoderBlock2 = rhs.senseAmpMuxLev2PredecoderBlock2;
	if (memoryType == tag && internalSenseAmp)
		comparator = rhs.comparator;

    tsvArray = rhs.tsvArray;

	return *this;
}
