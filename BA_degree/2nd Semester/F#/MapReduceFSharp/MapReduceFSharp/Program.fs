//Map Reduce
//Counting evens

let numbers =[0..10000000]

let res =
    numbers
    |> List.map(fun x -> if x % 7 = 0 then 1 else 0)
    |> List.fold (+) 0
    
printfn""
printfn"Piping: |> map evens |> sum ones= %A" res 
