import { useParams } from "react-router-dom";
import { TraceBoard, Transaction } from "../components/";
import { TraceProps } from "../components/Trace";
import { TransactionResultProp } from "../components/Transaction";

export default function TransactionDetail() {
  const { transactionId } = useParams();

  const txnResult: TransactionResultProp = {
    exeStatus: true,
    from: "",
    to: "",
    gasPrice: 0,
    value: 0,
    maxPriorityFeePerGas: 0,
    maxFeePerGas: 0,
    gasLimit: 0,
    gasUsage: 0,
    inputData: "",
    transactionFee: 0,
  };
  const traces: TraceProps[] = [];

  return (
    <div>
      <TraceBoard traces={traces} />
      <Transaction
        exeStatus={txnResult.exeStatus}
        from={txnResult.from}
        to={txnResult.to}
        gasPrice={txnResult.gasPrice}
        value={txnResult.value}
        transactionFee={txnResult.gasPrice * txnResult.gasUsage}
        maxPriorityFeePerGas={txnResult.maxPriorityFeePerGas}
        maxFeePerGas={txnResult.maxFeePerGas}
        gasUsage={txnResult.gasUsage}
        gasLimit={txnResult.gasLimit}
        inputData={txnResult.inputData}
      />
    </div>
  );
}
