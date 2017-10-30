import Ngl, datetime, os, calendar
import numpy as np
from netCDF4 import date2num,date2index
from netCDF4 import Dataset
#########################
datadir='/run/media/vgensini/Victor_4TB/narr/scp/'


###############################
#Enter the start and end date:#
######################################
start_input = '1979050321' #YYYYMMDDHH
end_input  =  '2016050321' #YYYYMMDDHH
######################################
begdate = datetime.datetime.strptime(start_input,"%Y%m%d%H") 
enddate = datetime.datetime.strptime(end_input,"%Y%m%d%H")
dates = []
while begdate <= enddate:
	if calendar.isleap(begdate.year) == True:
		begdate+=datetime.timedelta(days=1)
		dates.append(begdate)
	else:
		dates.append(begdate)
	begdate+=datetime.timedelta(days=365)
print dates
nc1 = Dataset('/run/media/vgensini/Victor_4TB/narr/narr_conv/narr_conv_20161201_0000.nc','r',format='NETCDF4_CLASSIC')
lats = nc1.variables["lats"][0][:][:]
lons = nc1.variables["lons"][0][:][:]
nc1.close()
scp_climo = np.empty((0,277,349))
for i,dt in enumerate(dates):
	nc = Dataset(datadir+'scp_narr_%s.nc' % str(dt.year),'r',format='NETCDF4_CLASSIC')
	idex = date2index(dt,nc['time'])
	scp = nc.variables["scp"][idex][:][:]
	cin  = nc.variables["sbcin"][idex][:][:]
	#cin mask
	term5 = np.fabs(cin)
	term5[np.fabs(cin)>50]=0.
	term5[np.fabs(cin)<=50]=1.
	scp = scp * term5
	scp_climo = np.append(scp_climo,[scp],axis=0)
	nc.close()
mean_scp = np.max(scp_climo,axis=0)
#print mean_scp.shape
#print len(dates)
wkres           =  Ngl.Resources()          #-- generate an resources object for workstation
wkres.wkWidth   =  2500                     #-- plot resolution 2500 pixel width
wkres.wkHeight  =  2000                     #-- plot resolution 2500 pixel height
wks_type        = "png"                     #-- graphics output type
wks             =  Ngl.open_wks(wks_type,"test",wkres)
#-- create 1st plot: vectors on global map
res                           =  Ngl.Resources()
res.mpFillOn               = True
res.mpOutlineOn            = True
res.mpLandFillColor        = "transparent"
res.mpOceanFillColor       = "grey"          # No fill
res.mpInlandWaterFillColor = "grey"
res.mpFillDrawOrder        = "PostDraw"
res.mpGridAndLimbOn        = True
#---Contour options
res.mpProjection = "LambertConformal"
res.cnLevelSelectionMode = "ManualLevels"
res.cnMinLevelValF       = 1
res.cnMaxLevelValF       = 20
res.cnLevelSpacingF      = 1
res.cnFillOn          = True          # turn on contour fill
res.cnLinesOn         = False         # turn off contour lines
res.cnLineLabelsOn    = False         # turn off line labels
res.cnFillMode        = "RasterFill"        # These two resources
res.trGridType        = "TriangularMesh"    # can speed up plotting.
res.cnFillPalette     = "precip3_16lev"
res.mpOutlineBoundarySets     = "GeophysicalAndUSStates"
res.mpLimitMode               = "Corners"                     #-- select a sub-region
res.mpLeftCornerLonF          =  -120                #-- left longitude value
res.mpRightCornerLonF         =  -60           #-- right longitude value
res.mpLeftCornerLatF          =  20                #-- left latitude value
res.mpRightCornerLatF         =  50           #-- right latitude value
res.lbOrientation     = "horizontal"   # default is vertical
res.sfXArray = lons
res.sfYArray = lats
res.tiMainString      = "April 27th Maximum SCP value (all years)"
res.tiMainFontHeightF = 0.015
res.mpLambertParallel1F = 33
res.mpLambertParallel2F = 45
res.mpLambertMeridianF = -95
plot = Ngl.contour_map(wks,mean_scp,res)
Ngl.end()