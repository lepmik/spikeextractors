import numpy as np
import os, sys
import unittest
import tempfile
import shutil
def append_to_path(dir0): # A convenience function
    if dir0 not in sys.path:
        sys.path.append(dir0)
append_to_path(os.getcwd()+'/..')
import spikeinterface as si
 
class TestExtractors(unittest.TestCase):
    def setUp(self):
        self.RX, self.SX, self.example_info = self._create_example()
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def _create_example(self):
        M=4
        N=10000
        samplerate=30000
        X=np.random.normal(0,1,(M,N))
        geom=np.random.normal(0,1,(M,2))
        RX=si.NumpyRecordingExtractor(timeseries=X,samplerate=samplerate,geom=geom)
        SX=si.NumpySortingExtractor()
        L=200
        train1=np.random.uniform(0,N,L)
        SX.addUnit(unit_id=1,times=train1)
        SX.addUnit(unit_id=2,times=np.random.uniform(0,N,L))
        SX.addUnit(unit_id=3,times=np.random.uniform(0,N,L))
        example_info=dict(
            M=M,
            N=N,
            samplerate=samplerate,
            unit_ids=[1,2,3],
            train1=train1
        )
        return (RX,SX,example_info)

    def test_example(self):
        self.assertEqual(self.RX.getNumChannels(),self.example_info['M'])
        self.assertEqual(self.RX.getNumFrames(),self.example_info['N'])
        self.assertEqual(self.RX.getSamplingFrequency(),self.example_info['samplerate'])
        self.assertEqual(self.SX.getUnitIds(),self.example_info['unit_ids'])
        self.assertTrue(np.allclose(self.SX.getUnitSpikeTrain(1),self.example_info['train1']))
     
    def test_mda_extractor(self):
        path1=self.test_dir+'/mda'
        path2=path1+'/firings_true.mda'
        si.MdaRecordingExtractor.writeRecording(self.RX,path1)
        si.MdaSortingExtractor.writeSorting(self.SX,path2)
        RX_mda=si.MdaRecordingExtractor(path1)
        SX_mda=si.MdaSortingExtractor(path2)
        self._check_recordings_equal(self.RX,RX_mda)
        self._check_sortings_equal(self.SX,SX_mda)

    def _check_recordings_equal(self,RX1,RX2):
        M=RX1.getNumChannels()
        N=RX1.getNumFrames()
        # getNumChannels
        self.assertEqual(RX1.getNumChannels(),RX2.getNumChannels())
        # getNumFrames
        self.assertEqual(RX1.getNumFrames(),RX2.getNumFrames())
        # getSamplingFrequency
        self.assertEqual(RX1.getSamplingFrequency(),RX2.getSamplingFrequency())
        # getTraces
        self.assertTrue(np.allclose(
            RX1.getTraces(),
            RX2.getTraces())
        )
        sf=0; ef=0; ch=[0,M-1]
        self.assertTrue(np.allclose(
            RX1.getTraces(start_frame=sf,end_frame=ef,channel_ids=ch),
            RX2.getTraces(start_frame=sf,end_frame=ef,channel_ids=ch)
        ))
        # getChannelInfo
        for m in range(M):
            self.assertTrue(np.allclose(
                np.array(RX1.getChannelInfo(channel_id=m)['location']),
                np.array(RX2.getChannelInfo(channel_id=m)['location'])
            ))
        # timeToFrame / frameToTime
        self.assertEqual(RX1.timeToFrame(12),RX2.timeToFrame(12))
        self.assertEqual(RX1.timeToFrame(1),RX2.timeToFrame(1))
        # getSnippets
        frames=[0,30,80]
        snippets1=RX1.getSnippets(snippet_len=20,center_frames=frames)
        snippets2=RX2.getSnippets(snippet_len=20,center_frames=frames)
        for ii in range(len(frames)):
            self.assertTrue(np.allclose(snippets1[ii],snippets2[ii]))

    def _check_sortings_equal(self,SX1,SX2):
        K=len(SX1.getUnitIds())
        # getUnitIds
        ids1=np.sort(np.array(SX1.getUnitIds()))
        ids2=np.sort(np.array(SX2.getUnitIds()))
        self.assertTrue(np.allclose(ids1,ids2))
        for id in ids1:
            train1=np.sort(SX1.getUnitSpikeTrain(id))
            train2=np.sort(SX2.getUnitSpikeTrain(id))
            self.assertTrue(np.allclose(train1,train2))
 
if __name__ == '__main__':
    unittest.main()
