"""Independent NumPy/SciPy references for the new controllability mathematics (one Node batch)."""
import json
from pathlib import Path
import subprocess
import numpy as np
from scipy.linalg import svdvals

ROOT=Path(__file__).resolve().parents[1]


def main():
    rng=np.random.default_rng(41)
    cases=[]
    for n in range(2,6):
        for q in range(1,4):
            for _ in range(12):
                cases.append(dict(A=rng.normal(size=(n,n)).tolist(),B=rng.normal(size=(n,q)).tolist()))
    for c in [-2,-1,0,1e-10,1e-7,0.5,1,2]:
        for b1 in [-2,-1,0,1,2]:
            for b2 in [-2,0,1,2]:
                for dual in [False,True]:
                    st=dict(c=c,b1=b1,b2=b2,dual=dual,alpha=0.7,beta=-1.2)
                    cases.append(dict(A=[[1,c],[0,2]],B=[[1,b1],[0,b2]] if dual else [[b1],[b2]],st=st))
    for eps in [0,1e-14,1e-10,1e-8,1e-4]:
        cases.append(dict(A=[[1,0],[0,2]],B=[[eps],[eps]]))
    js=r'''const fs=require('fs'),M=require('./courses/controls/controllability/dist/study_math.js');
const cases=JSON.parse(fs.readFileSync(0,'utf8'));
console.log(JSON.stringify(cases.map(c=>({info:M.controllability(c.A,c.B),
  model:c.st?M.explorerModel(c.st):null,
  discrete:c.st?M.discreteTwoSteps(c.A,[c.st.b1,c.st.b2],c.st.beta,c.st.alpha):null}))));'''
    proc=subprocess.run(['node','-e',js],cwd=ROOT,input=json.dumps(cases),capture_output=True,text=True,check=True)
    got=json.loads(proc.stdout);max_sv_error=0
    for i,(case,row) in enumerate(zip(cases,got)):
        A,B=np.array(case['A'],float),np.array(case['B'],float)
        n=len(A);C=np.concatenate([np.linalg.matrix_power(A,k)@B for k in range(n)],axis=1)
        info=row['info'];np.testing.assert_allclose(info['C'],C,rtol=1e-12,atol=1e-12,err_msg=f'C case {i}')
        s=np.pad(svdvals(C),(0,max(0,n-min(C.shape))))
        np.testing.assert_allclose(info['sigma'],s,rtol=1e-8,atol=2e-12,err_msg=f'SVD case {i}')
        max_sv_error=max(max_sv_error,float(np.max(np.abs(s-info['sigma']))))
        rank=int(np.count_nonzero(s>1e-9*s[0])) if s[0]>1e-12 else 0
        assert rank==info['rank'],(i,rank,info)
        assert info['controllable']==(rank==n)
        U=np.array(info['U']);np.testing.assert_allclose(U@U.T,np.eye(n),atol=2e-12)
        for u,sv in zip(U,s):
            np.testing.assert_allclose(C@C.T@u,sv*sv*u,atol=2e-11*max(1,s[0]**2),rtol=2e-10)
        if row['model']:
            st=case['st'];b=np.array([st['b1'],st['b2']]);point=st['alpha']*b+st['beta']*A@b
            np.testing.assert_allclose(row['model']['point'],point,atol=1e-12)
            np.testing.assert_allclose(row['discrete']['x2'],point,atol=1e-12)
            assert row['model']['rank']==rank
            if not st['dual']:np.testing.assert_allclose(row['model']['det'],np.linalg.det(C),atol=1e-12)
            if row['model']['w']:
                assert np.linalg.norm(np.array(row['model']['w'])@C)<=2e-9*max(1,np.linalg.norm(C))
    # Exact lecture examples and an uncontrollable eigenvector with nonzero B components.
    for c,b1,b2,rank in [(0,0,1,1),(1,0,1,2),(0,1,1,2),(1,1,1,1),(0,0,0,0)]:
        found=next(r for cse,r in zip(cases,got) if cse.get('st')==dict(c=c,b1=b1,b2=b2,dual=False,alpha=0.7,beta=-1.2))
        assert found['info']['rank']==rank
    print(json.dumps(dict(passed=True,cases=len(cases),max_singular_value_absolute_error=max_sv_error)))


if __name__=='__main__': main()
