import numpy as np
import os
import time
import align_cloud
from mayavi import mlab


def readFile(device, idx):
	dict = './../Save_Point_Cloud/'+str(device)+'/'
	filename_log = dict+str(idx).zfill(3)+'_log.txt'
	waiting = False
	while not os.path.exists(filename_log):
		if idx == 0:
			if not waiting:
				print "waiting for new data"
				waiting = True
		else:
			idx -= 1
			filename_log = dict+str(idx).zfill(3)+'_log.txt'
		time.sleep(0.001)
	time.sleep(1)
	#try:
	fp = open(filename_log, 'r')
	cargo_idx = int(fp.readline())
	image_num = int(fp.readline())
	fp.close()
	print "read in cargo " + str(idx)
	'''
	data = []
	for i in range(image_num):
		filename = dict+str(idx).zfill(3)+'_pc_offset_'+str(i).zfill(4)+'.npy'
		metaData = np.load(filename)
		print metaData.shape
		data.append(metaData)
	'''
	filename = dict+str(idx).zfill(3)+'_pc_offset.npy'
	data = np.load(filename)
	#except:
		#print "failure" + filename_log
	return data, image_num, idx


if __name__ == '__main__':
	idx = 0
	x = np.array([-1, 1])
	y = np.array([-1, 1])
	z = np.array([0, 2])
	scalars = -y
	plt = mlab.points3d(x, y, z, scalars, colormap="RdYlBu", scale_factor=0.01, scale_mode='none')
	
	@mlab.animate(delay=50)
	def anim(idx):
		
		while True:
			for device in range(2):
				rawData, image_num, idx = readFile(device, idx)
				x, y, z = np.array([[],[],[]])
				for data in rawData:
					x_new, y_new, z_new = np.transpose(data)
					x = np.hstack([x, x_new])
					y = np.hstack([y, y_new])
					z = np.hstack([z, z_new])
					scalars = -y
					plt.mlab_source.reset(x=x, y=y, z=z, scalars=scalars)
					mlab.title('device '+str(device))
					yield
				time.sleep(1)
			
			data = align_cloud.alignPointCloud(idx)
			x, y, z = np.transpose(data)
			scalars = -y
			plt.mlab_source.reset(x=x, y=y, z=z, scalars=scalars)
			mlab.title('aligned device')
			yield
			time.sleep(2)
			
			idx += 1

	print "Start ploting ..."
	anim(idx)
	mlab.view(180, 180)
	mlab.show(stop=True)
