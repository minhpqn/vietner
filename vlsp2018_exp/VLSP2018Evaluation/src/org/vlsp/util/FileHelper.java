package org.vlsp.util;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FilenameFilter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;
import java.io.Writer;
import java.net.URL;
import java.nio.MappedByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;
import java.util.Set;
import java.util.TreeSet;
import java.util.Vector;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class FileHelper {
  public static final class NullWriter extends Writer {

    private boolean open = true;

    private void ensureOpen() {
      if (!open)
        throw new IllegalStateException("Writer closed");
    }

    @Override
    public void close() throws IOException {
      open = false;
    }

    @Override
    public void flush() throws IOException {
      ensureOpen();
    }

    @Override
    public void write(char[] cbuf, int off, int len) throws IOException {
      if (cbuf == null)
        throw new NullPointerException();
      if (off < 0 || len < 0 || off + len > cbuf.length)
        throw new IllegalArgumentException();
      ensureOpen();
    }

    @Override
    public Writer append(char c) throws IOException {
      ensureOpen();
      return this;
    }

    @Override
    public Writer append(CharSequence csq) throws IOException {
      if (csq == null)
        throw new NullPointerException();
      ensureOpen();
      return this;
    }

    @Override
    public Writer append(CharSequence csq, int start, int end) throws IOException {
      if (csq == null)
        throw new NullPointerException();
      if (start < 0 || start > end || end > csq.length())
        throw new IllegalArgumentException();
      ensureOpen();
      return this;
    }

    @Override
    public void write(char[] cbuf) throws IOException {
      ensureOpen();
    }

    @Override
    public void write(int c) throws IOException {
      ensureOpen();
    }

    @Override
    public void write(String str) throws IOException {
      ensureOpen();
    }

    @Override
    public void write(String str, int off, int len) throws IOException {
      ensureOpen();
    }

    public boolean isOpen() {
      return open;
    }

    public void setOpen(boolean open) {
      this.open = open;
    }
  }

  public static class NullOutputStream extends OutputStream {
    @Override
    public void write(int b) throws IOException {
      // do nothing
    }

    @Override
    public void write(byte[] b, int off, int len) throws IOException {
      // do nothing
    }

    @Override
    public void write(byte[] b) throws IOException {
      // do nothing
    }
  }

  public static class ZeroInputStream extends InputStream {
    @Override
    public int read() throws IOException {
      return 0;
    }

    @Override
    public int read(byte[] b, int off, int len) throws IOException {
      len = Math.max(len, b.length - off);
      Arrays.fill(b, off, off + len, (byte) 0);
      return len;
    }
  }

  /**
   * @throws FileNotFoundException
   * @note use {@link #getBufferedFileReader(File, Charset)} for more explicit behavior
   */
  public static BufferedReader getBufferedFileReader(String filename) throws FileNotFoundException {
    if (filename == null)
      throw new NullPointerException();
    return getBufferedFileReader(new File(filename), Charset.defaultCharset());
  }

  /**
   * @throws FileNotFoundException
   */
  public static BufferedReader getBufferedFileReader(File file, Charset cs)
      throws FileNotFoundException {
    if (file == null)
      throw new NullPointerException();
    return getBufferedInputStreamReader(new FileInputStream(file), cs);
  }

  /**
   * @throws FileNotFoundException
   */
  public static BufferedReader getBufferedInputStreamReader(InputStream is, Charset cs) {
    try {
      return new BufferedReader(new InputStreamReader(is, cs.name()));
    } catch (UnsupportedEncodingException e) {
      throw new RuntimeException(e);
    }
  }

  /**
   * @throws FileNotFoundException
   * @throws UnsupportedEncodingException
   */
  public static BufferedWriter getBufferedFileWriter(String filename)
      throws UnsupportedEncodingException, FileNotFoundException {
    return getBufferedFileWriter(new File(filename), Charset.defaultCharset());
  }

  /**
   * @throws FileNotFoundException
   */
  public static BufferedWriter getBufferedFileWriter(File file, Charset cs)
      throws FileNotFoundException {
    if (file == null)
      throw new NullPointerException();
    return getBufferedOutputStreamWriter(new FileOutputStream(file), cs);
  }

  public static BufferedWriter getBufferedFileAppend(File file, Charset cs)
      throws FileNotFoundException {
    if (file == null)
      throw new NullPointerException();
    return getBufferedOutputStreamWriter(new FileOutputStream(file, true), cs);
  }

  public static BufferedWriter getBufferedOutputStreamWriter(OutputStream os, Charset cs)
      throws FileNotFoundException {
    try {
      return new BufferedWriter(new OutputStreamWriter(os, cs.name()));
    } catch (UnsupportedEncodingException e) {
      throw new RuntimeException(e);
    }
  }

  /**
   *
   * @param file1
   * @param file2
   * @param outfile
   * @param charset
   * @author illes
   * @throws IOException
   */
  public static void concatenateFiles(File file1, File file2, File outfile, Charset charset)
      throws IOException {
    if (charset == null)
      charset = Charset.defaultCharset();

    PrintWriter pw = new PrintWriter(outfile, charset.name());
    pw.write(readFileAsString(file1, charset));
    pw.write(readFileAsString(file2, charset));
    pw.close();
  }

  public static void concatenateFiles(String file1, String file2, String outfile, Charset charset)
      throws IOException {
    concatenateFiles(new File(file1), new File(file2), new File(outfile), charset);
  }

  /**
   * Reads a Java object from the given file.
   *
   * @param FILE
   * @return
   */
  public static Object readObjectFromFile(File FILE) {
    Object result = null;
    try {
      ObjectInputStream ois = new ObjectInputStream(new FileInputStream(FILE));
      result = ois.readObject();
      ois.close();
    } catch (Exception e) {
      e.printStackTrace();
    }
    return result;
  }

  /**
   * Writes a Java object to the given file.
   *
   * @param o
   * @param FILE
   */
  public static void writeObjectToFile(Object o, File FILE) {
    try {
      FileOutputStream fos = null;
      ObjectOutputStream out = null;
      fos = new FileOutputStream(FILE);
      out = new ObjectOutputStream(fos);
      out.writeObject(o);
      out.close();
    } catch (Exception e) {
      e.printStackTrace();
    }
  }

  public static String[] readFileAsLines(File file, Charset charset) {
    return readFileAsList(file, charset).toArray(new String[0]);
  }

  public static String[] readURLAsLines(URL url, Charset charset) {
    List<String> content = new LinkedList<String>();
    try {
      BufferedReader in =
          new BufferedReader(new InputStreamReader(url.openStream(), charset.name()));
      String line;
      while ((line = in.readLine()) != null)
        content.add(line);
      in.close();
      in = null;
    } catch (IOException ioe) {
      ioe.printStackTrace();
      return null;
    }
    return content.toArray(new String[0]);
  }

  public static List<String> readFileAsList(File file, Charset charset) {
    List<String> content = new LinkedList<String>();
    try {
      BufferedReader in =
          new BufferedReader(new InputStreamReader(new FileInputStream(file), charset.name()));
      String line;
      while ((line = in.readLine()) != null)
        content.add(line);
      in.close();
      in = null;
    } catch (IOException ioe) {
      ioe.printStackTrace();
      return null;
    }
    return content;
  }

  public static List<String> readFileAsListSubstractList(File file, List<String> list,
      Charset charset) {
    List<String> content = new LinkedList<String>();
    try {
      BufferedReader in =
          new BufferedReader(new InputStreamReader(new FileInputStream(file), charset.name()));
      String line;
      while ((line = in.readLine()) != null)
        if (!list.contains(line))
          content.add(line);
      in.close();
      in = null;
    } catch (IOException ioe) {
      ioe.printStackTrace();
      return null;
    }
    return content;
  }

  public static Queue<String> readFileAsQueue(File file, Charset charset) {
    Queue<String> content = new LinkedList<String>();
    try {
      BufferedReader in =
          new BufferedReader(new InputStreamReader(new FileInputStream(file), charset.name()));
      String line;
      while ((line = in.readLine()) != null)
        content.add(line);
      in.close();
      in = null;
    } catch (IOException ioe) {
      ioe.printStackTrace();
      return null;
    }
    return content;
  }

  public static Set<String> readFileAsSetSubstractSet(File file, Set<String> set, Charset charset) {
    Set<String> content = new HashSet<String>();
    try {
      BufferedReader in =
          new BufferedReader(new InputStreamReader(new FileInputStream(file), charset.name()));
      String line;
      int count = 1;
      while ((line = in.readLine()) != null) {
        if (count % 1000000 == 0)
          System.out.println(count);
        if (!set.contains(line))
          content.add(line);
        count++;
      }
      in.close();
      in = null;
    } catch (IOException ioe) {
      ioe.printStackTrace();
      return null;
    }
    return content;
  }

  public static Set<Long> readFileIntoLongSet(String filename) throws IOException {
    Set<Long> s = new HashSet<Long>();
    BufferedReader in =
        new BufferedReader(new InputStreamReader(new FileInputStream(filename), "UTF-8"));
    String line;
    while ((line = in.readLine()) != null)
      s.add(Long.parseLong(line.toLowerCase()));

    in.close();
    in = null;
    return s;
  }

  public static Set<String> readFileIntoSet(String filename, boolean toLowerCase)
      throws IOException {
    Set<String> s = new TreeSet<String>();
    BufferedReader in =
        new BufferedReader(new InputStreamReader(new FileInputStream(filename), "UTF-8"));
    String line;
    while ((line = in.readLine()) != null)
      if (toLowerCase)
        s.add(line.toLowerCase());
      else
        s.add(line);

    in.close();
    in = null;
    return s;
  }

  public static Set<String> readFileIntoTreeSet(String filename, boolean toLowerCase)
      throws IOException {
    Set<String> s = new TreeSet<String>();
    BufferedReader in =
        new BufferedReader(new InputStreamReader(new FileInputStream(filename), "UTF-8"));
    String line;
    while ((line = in.readLine()) != null)
      if (toLowerCase)
        s.add(line.toLowerCase());
      else
        s.add(line);

    in.close();
    in = null;
    return s;
  }

  public static Set<String> readFileIntoSet(String filename, boolean toLowerCase,
      boolean plusFirstCharacterUpperCaseVariant) {
    Set<String> s = new HashSet<String>();
    try {
      BufferedReader in =
          new BufferedReader(new InputStreamReader(new FileInputStream(filename), "UTF-8"));
      String line;
      while ((line = in.readLine()) != null) {
        if (line.length() > 0 && !line.startsWith("#")) {
          if (toLowerCase) {
            line = line.toLowerCase();
            s.add(line);
          } else {
            s.add(line);
          }
          if (plusFirstCharacterUpperCaseVariant) {
            char firstChar = Character.toUpperCase(line.charAt(0));
            s.add(firstChar + line.substring(1));
          }
        }
      }
      in.close();
      in = null;
    } catch (IOException ioe) {
      ioe.printStackTrace();
      return null;
    }
    return s;
  }

  /**
   * Reads a file into a string array, one line per element.
   *
   * @param filename - the file to read
   * @return content as string array
   */
  public static String[] readFromFile(File file) {
    List<String> content = new LinkedList<String>();
    try {
      BufferedReader in =
          new BufferedReader(new InputStreamReader(new FileInputStream(file), "UTF-8"));
      String line;
      while ((line = in.readLine()) != null)
        content.add(line);
      in.close();
      in = null;
    } catch (IOException ioe) {
      ioe.printStackTrace();
      return null;
    }
    // String[] result = new String[content.size()];
    // for (int i = 0; i < content.size(); i++) {
    // result[i] = (String)content.get(i);
    // }
    // content.clear();
    // content = null;
    // return result;
    return content.toArray(new String[0]);
  }

  /**
   * Reads a file into a string array, one line per element.
   *
   * @param filename - the file to read
   * @return content as string array
   */
  public static String[] readFromFile(String filename) {
    return readFromFile(new File(filename));
  }

  public static boolean appendToFile(String content, File file, Charset cs) throws IOException {
    Writer w = getBufferedFileAppend(file, cs);
    w.write(content);
    w.close();
    return true;
  }

  /**
   * Write the string into a file
   *
   * @param content
   * @param filename
   * @return boolean
   * @throws IOException
   */
  public static boolean writeToFile(String content, File file, Charset cs) throws IOException {
    Writer w = getBufferedFileWriter(file, cs);
    w.write(content);
    w.close();
    return true;
  }

  /**
   * Write the string array into a file, each element on a separate line
   *
   * @param content
   * @param filename
   * @return boolean
   * @throws IOException
   */
  public static boolean writeToFile(String[] content, File file, Charset cs) throws IOException {

    BufferedWriter w = getBufferedFileWriter(file, cs);

    if (content.length > 0) {
      // write all but the last element into the file,
      // with trailing newlines
      for (int i = 0; i < (content.length - 1); i++) {
        w.write(content[i] + "\n");
      }
      // write the last element, without newline
      w.write(content[content.length - 1]);
    }

    w.close();
    w = null;

    return true;
  }

  /**
   * Write the string array into a file, each element on a separate line
   *
   * @param content
   * @param filename
   * @return boolean
   */
  public static boolean writeSetToFile(Set<String> content, String filename) {
    try {

      List<String> contentList = new ArrayList<String>(content.size());
      for (String string : content) {
        contentList.add(string);
      }
      Collections.sort(contentList);

      PrintWriter pw = new PrintWriter(filename, "UTF-8");

      if (content.size() > 0) {
        // write all but the last element into the file,
        // with trailing newlines
        for (String string : contentList) {
          pw.write(string + "\n");
        }
      }

      pw.close();
      pw = null;

    } catch (IOException ioe) {
      ioe.printStackTrace();
      return false;
    }

    return true;
  }

  public static boolean writeListToFile(List<String> content, String filename) {
    try {
      PrintWriter pw = new PrintWriter(filename, "UTF-8");

      if (content.size() > 0) {
        for (String string : content) {
          pw.write(string + "\n");
        }
      }

      pw.close();
      pw = null;

    } catch (IOException ioe) {
      ioe.printStackTrace();
      return false;
    }

    return true;
  }

  public static boolean writeCollectionToFile(Collection<String> content, String filename) {
    try {
      PrintWriter pw = new PrintWriter(filename, "UTF-8");

      if (content.size() > 0) {
        for (String string : content) {
          pw.write(string + "\n");
        }
      }

      pw.close();
      pw = null;

    } catch (IOException ioe) {
      ioe.printStackTrace();
      return false;
    }

    return true;
  }

  /**
   * Write the vector into a file, each element on a separate line.
   *
   * @param content - the vector
   * @param filename - the name of the file
   * @return boolean - true if writing was successful
   */
  public static boolean writeToFile(Vector<String> content, File file) {
    try {

      PrintWriter pw = new PrintWriter(file, "UTF-8");

      if (content.size() > 0) {
        // write all but the last element into the file,
        // with trailing newlines
        for (int i = 0; i < (content.size() - 1); i++) {
          pw.write((String) content.get(i) + "\n");
        }
        // write the last element, without newline
        pw.write((String) content.get(content.size() - 1));
      }

      pw.close();
      pw = null;

    } catch (IOException ioe) {
      ioe.printStackTrace();
      return false;
    }

    return true;
  }

  /**
   * Returns the names of all files found in the specified directory
   *
   * @param dirname
   * @return String[]
   */
  public static String[] getFilenamesFromDirectory(String dirname) {
    File dir = new File(dirname);
    String[] files = dir.list(new FilenameFilter() {
      public boolean accept(File dir, String name) {
        return true;
      }
    });
    return files;
  }

  /**
   * Returns the names of all files found in the specified directory. If <tt>recursively</tt> is
   * true, returns files in subdirectories as well. Uses the current setting for the file filter
   * expression (change/get it using the methods <tt>setFilefilterExpression(String)</tt> and
   * <tt>getFilefilterExpression()</tt>), and returns file names fitting this expression only (no
   * directories etc.).
   *
   * @param dirname
   * @param recursively
   * @return String[]
   */
  public static String[] getFilenamesFromDirectory(String dirname, boolean recursively) {
    if (!recursively) {
      File dir = new File(dirname);
      return dir.list(onlyFilenamesFilterWithExpression);
    } else {
      return listFiles(new File(dirname), (List<String>) new ArrayList<String>());
    }
  }

  /**
   * Returns the names of all files found in the specified directory and matching the given
   * expression. If <tt>recursively</tt> is true, returns files in subdirectories as well.
   *
   * @param dirname
   * @param recursively
   * @param expression
   * @return String[]
   */
  public static String[] getFilenamesFromDirectory(String dirname, boolean recursively,
      String expression) {
    String storeFilter = getFilefilterExpression();
    setFilefilterExpression(expression);
    String[] ret = getFilenamesFromDirectory(dirname, recursively);
    setFilefilterExpression(storeFilter);
    return ret;
  }

  /**
   * Sets a new value for the default file filter expression.<br>
   * Default is &quot;.*&quot;
   *
   * @param exp
   */
  public static void setFilefilterExpression(String exp) {
    filefilterExpression = exp;
  }

  /**
   * Returns the current setting for the file filter expression.
   *
   * @return String
   */
  public static String getFilefilterExpression() {
    return filefilterExpression;
  }

  /**
   * Returns an array containing all files in this directory and any subdirectory.
   *
   * @param directory
   * @param filenames
   * @return String[] - list of files
   */
  public static String[] listFiles(String directory) {
    File f = new File(directory);
    if (f.isFile())
      return null;

    List<String> holder = new ArrayList<String>();

    File[] dirFiles = f.listFiles();
    for (int i = 0; i < dirFiles.length; i++) {
      File file = dirFiles[i];

      if (!file.isDirectory()) {
        holder.add(file.getAbsolutePath());
      }
    }
    return holder.toArray(new String[holder.size()]);
  }

  /**
   * Returns an array containing all files in this directory and any subdirectory.
   *
   * @param directory
   * @param filenames
   * @return String[] - list of files
   */
  public static String[] listFiles(File directory, List<String> filenames) {
    File[] dirFiles = directory.listFiles();
    for (int i = 0; i < dirFiles.length; i++) {
      File file = dirFiles[i];

      if (!file.isDirectory()) {
        filenames.add(file.getAbsolutePath());
      } else {
        listFiles(file, filenames);
      }
    }
    String[] files = new String[filenames.size()];
    return (String[]) filenames.toArray(files);
  }

  /**
   *
   * @param file
   * @return
   * @author Illes Solt
   * @throws IOException
   */
  public static String readFileAsString(File file) throws IOException {
    return readFileAsString(file, Charset.defaultCharset());
  }

  /**
   *
   * @param file
   * @param charset
   * @return
   * @author Illes Solt
   * @throws IOException
   */
  public static String readFileAsString(File file, Charset charset) throws IOException {
    byte[] contents = readFileAsBytes(file);

    try {
      return new String(contents, charset.name());
    } catch (UnsupportedEncodingException e) {
      throw new RuntimeException("wrong encoding: " + charset, e);
    }
  }

  /**
   * Efficiently read a file into a byte array.
   *
   * @param file
   * @return
   * @author Illes Solt
   * @throws IOException
   */
  protected static byte[] readFileAsBytes(File file) throws IOException {
    // ArrayList<ArrayList<?>> sequences = new ArrayList<ArrayList<?>>();

    // ArrayList<Integer> separators;
    byte[] contents = null;

    FileInputStream fis = null;
    try {
      fis = new FileInputStream(file);
      FileChannel fc = fis.getChannel();

      // Get the file's size and then map it into memory
      int sz = (int) fc.size();
      MappedByteBuffer bb = fc.map(FileChannel.MapMode.READ_ONLY, 0, sz);

      if (bb.hasArray()) {
        contents = bb.array();
      } else {
        // System.err.println("Oops, no array :(, falling back to
        // buffer.get(dst)...");
        contents = new byte[sz];
        bb.get(contents);
      }

    } catch (IOException e) {
      throw new RuntimeException("Error while trying to read file: " + file.getCanonicalPath(), e);
    } finally {
      if (fis != null)
        fis.close();
    }

    return contents;
  }

  /**
   * This file filter accepts only normal files, e.g. no directories. See java.io.File.isFile().
   */
  static FilenameFilter onlyFilenamesFilter = new FilenameFilter() {
    public boolean accept(File dir, String name) {
      File thefile = new File(dir.getAbsolutePath() + "/" + name);
      return thefile.isFile();
    }
  };

  /**
   * This file filter accepts only normal files that additionally match a file filter expression.
   * Get and set the current file filter expression with <tt>(g|s)etFilefilterExpression</tt>.
   * Default: &quot;<tt>.*</tt>&quot;
   */
  static FilenameFilter onlyFilenamesFilterWithExpression = new FilenameFilter() {
    public boolean accept(File dir, String name) {
      File thefile = new File(dir.getAbsolutePath() + "/" + name);
      return (thefile.isFile() && name.matches(filefilterExpression));
    }
  };

  /**
   * This file filter accepts only directories. See java.io.File.isDirectory().
   */
  static FilenameFilter onlyDirectorynamesFilter = new FilenameFilter() {
    public boolean accept(File dir, String name) {
      File thefile = new File(dir.getAbsolutePath() + "/" + name);
      return thefile.isDirectory();
    }
  };

  private static String filefilterExpression = ".*";

  /**
   * Convenience wrapper of {@link #readFileAsLines(File, Charset)}.
   */
  public static String[] readFileAsLines(String file) {
    return readFileAsLines(new File(file), Charset.defaultCharset());
  }

  private static abstract class PatternFilenameFilter implements FilenameFilter {
    private final Matcher m;

    public PatternFilenameFilter(Pattern pattern) {
      this.m = pattern.matcher("");
    }

    public PatternFilenameFilter(String regex) {
      this(Pattern.compile(regex));
    }

    /**
     *
     * @param filename
     * @return <code>true</code> iff the pattern matches the <b>whole</b> filename
     */
    protected boolean matches(String filename) {
      return m.reset(filename).matches();
    }
  }

  /**
   * Accepts all files whose whole basename is <b>not</b> matched by the given regular expression.
   *
   * @author illes
   *
   */
  public static class ExcludePatternFilenameFilter extends PatternFilenameFilter {
    public ExcludePatternFilenameFilter(String regex) {
      super(regex);
    }

    @Override
    public boolean accept(File dir, String name) {
      return !matches(name);
    }
  }

  /**
   * Accepts all files whose <b>whole</b> basename is matched by the given regular expression.
   *
   * @author illes
   *
   */
  public static class IncludePatternFilenameFilter extends PatternFilenameFilter {
    public IncludePatternFilenameFilter(String regex) {
      super(regex);
    }

    @Override
    public boolean accept(File dir, String name) {
      return matches(name);
    }
  }

  /**
   * Check if file is a directory and readable.
   *
   * @param dir
   */
  public static void checkDir(File dir) {
    if (!dir.exists() || !dir.isDirectory() || !dir.canRead())
      throw new RuntimeException("Error reading directory " + dir);
  }

  /**
   * Check if file is not a directory and readable.
   *
   * @param dir
   */
  public static void checkFile(File file) {
    if (!file.exists() || file.isDirectory() || !file.canRead())
      throw new RuntimeException("Error reading file " + file);
  }

}
