from cobaya.likelihoods.des_y3._cosmolike_prototype_base import _cosmolike_prototype_base
import cosmolike_des_y3_interface as ci

class des_3x2pt(_cosmolike_prototype_base):
	# ------------------------------------------------------------------------
	# ------------------------------------------------------------------------
	# ------------------------------------------------------------------------

	def initialize(self):
		super(des_3x2pt,self).initialize(probe="3x2pt")

	# ------------------------------------------------------------------------
	# ------------------------------------------------------------------------
	# ------------------------------------------------------------------------

	def logp(self, **params_values):
		self.set_cosmo_related()

		self.set_lens_related(**params_values)

		self.set_source_related(**params_values)

		if self.create_baryon_pca:
			self.generate_baryonic_PCA(**params_values)

		datavector = ci.compute_data_vector_masked()

		return self.compute_logp(datavector)

