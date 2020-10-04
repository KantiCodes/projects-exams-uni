//    let numbers = [0..50000000]
//    let oneBigArray = List.toArray numbers
    let rec slowdown n = if n=0 then 0 else slowdown(n-1)
    let oneBigArray = [| 0 .. 50000000 |]

    //Counting evens sequential:
    printfn "Starting sequential counting evens: %A" ""
    let res =
       oneBigArray 
       |> Array.map (fun x ->  ignore(slowdown(100))
                               if x % 2 = 0 then 1 else 0)
       |> Array.fold (+) 0
          
    printfn "Done sequential counting evens: %A" (res)

    //Counting evens parallel:
    printfn "Starting parallel counting evens: %A" ""
    let res1 =
       oneBigArray 
       |> Array.Parallel.map (fun x ->  ignore(slowdown(100))
                                        if x % 2 = 0 then 1 else 0)
       |> Array.fold (+) 0
          
    printfn "Done parallel counting evens: %A" (res1)

  