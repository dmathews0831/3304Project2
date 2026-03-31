{- 
As a Hokie, I, <YOUR NAME GOES HERE> ,  will conduct myself with honor and integrity at all times.  
I will not lie, cheat, or steal, nor will I accept the actions of those who do.”

"""
#############################################################################
################ DO NOT MODIFY THIS CODE ####################################
#############################################################################
-}

import System.Environment
import System.IO

main :: IO ()
main = do
        args <- getArgs
        let files = get_names args
        let input = fst files 
        let output = snd files
        in_handle <- openFile input ReadMode
        out_handle <- openFile output WriteMode
        mainloop in_handle out_handle
        hClose in_handle
        hClose out_handle

mainloop :: Handle -> Handle -> IO ()
mainloop in_handle out_handle = 
        do in_eof <- hIsEOF in_handle
           if in_eof
                then return ()
                else do line <- hGetLine in_handle
                        let line_words = words line
                        print $ evaluate line_words
                        hPutStrLn out_handle $ evaluate line_words
                        mainloop in_handle out_handle


get_names :: [String] -> (String, String)
get_names (arg1:arg2:_) = 
        let in_file = arg1
            out_file = arg2
        in (in_file, out_file)


-- converts String to Float 
stringToFloat :: String -> Float
stringToFloat a = read a :: Float


{-
#############################################################################
################ Write your code below this line ############################
#############################################################################
-}


-- Your implementation goes here. Feel free to add more functions.
evaluate :: [String] -> String
evaluate (a:xs) = unwords (a:xs)
evaluate [] = ""

