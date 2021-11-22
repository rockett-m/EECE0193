//Copyright (c) 2017-2019, IIT Hyderabad. See LICENSE file in the top-level directory
//Copyright (c) 2015-2016, UT-Battelle, LLC. See LICENSE file in the top-level directory
// This file contains code from NVSim, (c) 2012-2013,  Pennsylvania State University 
//and Hewlett-Packard Company. See LICENSE_NVSim file in the top-level directory.
//No part of DESTINY Project, including this file, may be copied,
//modified, propagated, or distributed except according to the terms
//contained in the LICENSE file.


#ifndef MEMCELL_H_
#define MEMCELL_H_

#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "typedef.h"

using namespace std;

class MemCell {
public:
	MemCell();
	virtual ~MemCell();

	/* Functions */
	void ReadCellFromFile(const std::string & inputFile);
    void ApplyPVT();
	void CellScaling(int _targetProcessNode);
	double GetMemristance(double _relativeReadVoltage);  /* Get the LRS resistance of memristor at log-linera region of I-V curve */
	void CalculateWriteEnergy();
	void CalculateShiftEnergy();
	double CalculateReadPower();
	void PrintCell(int indent = 0);

	/* Properties */
	string inputFileName;
	MemCellType memCellType;	/* Memory cell type (like MRAM, PCRAM, etc.) */
	MemCellLevel memCellLevel;	/* Memory cell storage level, SLC, MLC, TLC...*/
	int processNode;        /* Cell original process technology node, Unit: nm*/
	double area;			/* Cell area, Unit: F^2 */
	double aspectRatio;		/* Cell aspect ratio, H/W */
	double widthInFeatureSize;	/* Cell width, Unit: F */
	double heightInFeatureSize;	/* Cell height, Unit: F */
	double resistanceOn;	/* Turn-on resistance */
	double resistanceOff;	/* Turn-off resistance */
	double capacitanceOn;   /* Cell capacitance when memristor is on */
	double capacitanceOff;  /* Cell capacitance when memristor is off */
	bool   readMode;		/* true = voltage-mode, false = current-mode */
	double readVoltage;		/* Read voltage */
	double readCurrent;		/* Read current */
	double readPulse;		/* Read pulse*/
	double minSenseVoltage; /* Minimum sense voltage */
    double wordlineBoostRatio; /*TO-DO: function not realized: ratio of boost wordline voltage to vdd */
	double readPower;       /* Read power per bitline (uW)*/
	bool   resetMode;		/* true = voltage-mode, false = current-mode */
	double resetVoltage;	/* Reset voltage */
	double resetCurrent;	/* Reset current */
	double resetPulse;		/* Reset pulse duration (ns) */
	double resetEnergy;     /* Reset energy per cell (pJ) */
	bool   setMode;			/* true = voltage-mode, false = current-mode */
	double setVoltage;		/* Set voltage */
	double setCurrent;		/* Set current */
	double setPulse;		/* Set pulse duration (ns) */
	double setEnergy;       /* Set energy per cell (pJ) */
	CellAccessType accessType;	/* Cell access type: CMOS, BJT, or diode */

	/* Optional properties */
	int stitching;			/* If non-zero, add stitching overhead for every x cells */
	double gateOxThicknessFactor; /* The oxide thickness of FBRAM could be larger than the traditional SOI MOS */
	double widthSOIDevice; /* The gate width of SOI device as FBRAM element, Unit: F*/
	double widthAccessCMOS;	/* The gate width of CMOS access transistor, Unit: F */
	double voltageDropAccessDevice;  /* The voltage drop on the access device, Unit: V */
	double leakageCurrentAccessDevice;  /* Reverse current of access device, Unit: uA */
	double capDRAMCell;		/* The DRAM cell capacitance if the memory cell is DRAM, Unit: F */
	double widthSRAMCellNMOS;	/* The gate width of NMOS in SRAM cells, Unit: F */
	double widthSRAMCellPMOS;	/* The gate width of PMOS in SRAM cells, Unit: F */

	/* For memristor */
	bool readFloating;      /* If unselected wordlines/bitlines are floating to reduce total leakage */
	double resistanceOnAtSetVoltage; /* Low resistance state when set voltage is applied */
	double resistanceOffAtSetVoltage; /* High resistance state when set voltage is applied */
	double resistanceOnAtResetVoltage; /* Low resistance state when reset voltage is applied */
	double resistanceOffAtResetVoltage; /* High resistance state when reset voltage is applied */
	double resistanceOnAtReadVoltage; /* Low resistance state when read voltage is applied */
	double resistanceOffAtReadVoltage; /* High resistance state when read voltage is applied */
	double resistanceOnAtHalfReadVoltage; /* Low resistance state when 1/2 read voltage is applied */
	double resistanceOffAtHalfReadVoltage; /* High resistance state when 1/2 read voltage is applied */
	double resistanceOnAtHalfResetVoltage; /* Low resistance state when 1/2 reset voltage is applied */

	/* For NAND flash */
	double flashEraseVoltage;		/* The erase voltage, Unit: V, highest W/E voltage in ITRS sheet */
	double flashPassVoltage;		/* The voltage applied on the unselected wordline within the same block during programming, Unit: V */
	double flashProgramVoltage;		/* The program voltage, Unit: V */
	double flashEraseTime;			/* The flash erase time, Unit: s */
	double flashProgramTime;		/* The SLC flash program time, Unit: s */
	double gateCouplingRatio;		/* The ratio of control gate to total floating gate capacitance */

    /* For eDRAM. */
    double retentionTime;           /* Cell time to data loss (us) */
    double temperature;             /* Temperature for which the cell input values are valid. */

    /* For DWM	*/
    double shiftCurrent;			
    double shiftPulse;
    double shiftEnergy;
    double tapeLength;
    double portDistance;
    double tapePerGroup;

    /* For MLC	*/
    double avgIterations;
    double interval;

    /* For MLC MRAM*/

	double resetVoltageSoft;	/* Reset voltage */
	double resetCurrentSoft;	/* Reset current */
	double resetPulseSoft;		/* Reset pulse duration (ns) */
	double resetEnergySoft;     /* Reset energy per cell (pJ) */

	double setVoltageSoft;		/* Set voltage */
	double setCurrentSoft;		/* Set current */
	double setPulseSoft;		/* Set pulse duration (ns) */
	double setEnergySoft;       /* Set energy per cell (pJ) */
};

#endif /* MEMCELL_H_ */
