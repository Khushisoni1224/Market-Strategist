import { useCallback, useState } from 'react';
import { Plus, PackageOpen, Tag, ArrowUpRight } from 'lucide-react';
import { Workspace } from '../components/common/Workspace';
import { Button, EmptyState, LoadError, LoadingRows, PageHeading, Panel, useDemoLoad } from '../components/common/Elements';
import { AddProductModal, type NewProduct } from '../components/products/AddProductModal';
import { ProductTable } from '../components/products/ProductTable';
import { api } from '../services/api';

export default function Products() {
  const load=useCallback(()=>api.getProducts(),[]);const {data,loading,error,refresh}=useDemoLoad(load);const [modal,setModal]=useState(false);const [notice,setNotice]=useState('');
  async function addProduct(input:NewProduct){await api.addProduct(input);setModal(false);setNotice('Product added to your demo catalog.');refresh();}
  return <Workspace><PageHeading eyebrow="Your catalog" title="Products" description="Keep a clear view of what you sell and which products are showing promotion potential." action={<Button testId="button-add-product" onClick={()=>setModal(true)}><Plus size={15}/>Add product</Button>}/>
    {notice&&<div className="mb-5 rounded-xl border border-[#E5DDFB] bg-white px-4 py-3 text-xs font-semibold text-[#5318EB]" role="status" data-testid="status-product">{notice}</div>}
    <div className="mb-5 grid gap-3 sm:grid-cols-3"><Panel className="flex items-center gap-3 !p-4"><span className="grid h-10 w-10 place-items-center rounded-xl bg-[#F0EBFF] text-[#5318EB]"><PackageOpen size={18}/></span><div><div className="font-display text-xl font-extrabold">{loading?'—':data?.length??0}</div><div className="text-[11px] text-slate-500">Products tracked</div></div></Panel><Panel className="flex items-center gap-3 !p-4"><span className="grid h-10 w-10 place-items-center rounded-xl bg-[#F0EBFF] text-[#5318EB]"><ArrowUpRight size={18}/></span><div><div className="font-display text-xl font-extrabold">{loading?'—':data?.filter(p=>p.promotionPotential==='HIGH').length??0}</div><div className="text-[11px] text-slate-500">High potential signals</div></div></Panel><Panel className="flex items-center gap-3 !p-4"><span className="grid h-10 w-10 place-items-center rounded-xl bg-[#F0EBFF] text-[#5318EB]"><Tag size={18}/></span><div><div className="font-display text-xl font-extrabold">{loading?'—':data?.length?`$${Math.round(data.reduce((sum,p)=>sum+p.price,0)/data.length)}`:'—'}</div><div className="text-[11px] text-slate-500">Average price</div></div></Panel></div>
    <Panel><div className="mb-5"><h2 className="font-display text-base font-extrabold">Product catalog</h2><p className="mt-1 text-xs text-slate-500">Sample data for the Northline Goods demo business</p></div>{loading?<LoadingRows/>:error?<LoadError onRetry={refresh}/>:!data?.length?<EmptyState title="Your catalog is ready for its first product" text="Add a product to start connecting customer and performance signals." action={<Button testId="button-add-first-product" onClick={()=>setModal(true)}><Plus size={14}/>Add a product</Button>}/>:<ProductTable products={data}/>}</Panel>
    <AddProductModal open={modal} onClose={()=>setModal(false)} onSave={addProduct}/>
  </Workspace>;
}
