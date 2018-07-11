import numpy as np
import os
import time
from mayavi import mlab


def readFile(idx):
	dict = './../Save_Point_Cloud/0/'
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
	return data, image_num


if __name__ == '__main__':
	idx = 0
	x = np.array([-1, 1])
	y = np.array([-1, 1])
	z = np.array([0, 2])
	scalars = -y
	plt = mlab.points3d(x, y, z, scalars, colormap="RdYlBu", scale_factor=0.01, scale_mode='none')
	
	@mlab.animate(delay=10)
	def anim(idx):
		while True:
			rawData, image_num = readFile(idx)
			x, y, z = np.array([[],[],[]])
			for data in rawData:
				x_new, y_new, z_new = np.transpose(data)
				x = np.hstack([x, x_new])
				y = np.hstack([y, y_new])
				z = np.hstack([z, z_new])
				scalars = -y
				plt.mlab_source.reset(x=x, y=y, z=z, scalars=scalars)
				yield
			idx += 1


	anim(idx)
	mlab.view(180, 180)
	mlab.show(stop=True)
