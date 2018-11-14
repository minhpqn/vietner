package org.vlsp.ner;

import java.io.File;
import java.nio.charset.Charset;
import java.util.HashMap;
import java.util.Map;
import java.util.TreeMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.vlsp.util.FileHelper;


/**
 * @author vutm
 *
 */
public class VLSP2018MUCEvaluation {

  /**
   * @param args
   * @throws Exception
   */
  public static void main(String[] args) throws Exception {
    if (args.length < 2) {
      System.out.println("Usage: java -cp bin org/vlsp/ner/VLSP2018MUCEvaluation <goldAnswerFolder> <testFolder>");
      System.exit(1);
    }
    File annFolder = new File(args[0]);
    File testFolder = new File(args[1]);

    System.out.println("\n======================Nested evaluation=======================");
    eval(annFolder, testFolder);
  }

  public static void eval(File annFolder, File testFolder) throws Exception {
    int tpTotalPER = 0;
    int predTotalPER = 0;
    int annTotalPER = 0;

    int tpTotalLOC = 0;
    int predTotalLOC = 0;
    int annTotalLOC = 0;

    int tpTotalORG = 0;
    int predTotalORG = 0;
    int annTotalORG = 0;

    int overallTotalTP = 0;
    int overallTotalPRED = 0;
    int overallTotalANN = 0;

    for (File subFolder : annFolder.listFiles()) {
      System.out.println("-----------------------------");
      System.out.println(subFolder.getName());
      System.out.println("-----------------------------");

      int tpPER = 0;
      int predPER = 0;
      int annPER = 0;

      int tpLOC = 0;
      int predLOC = 0;
      int annLOC = 0;

      int tpORG = 0;
      int predORG = 0;
      int annORG = 0;

      int overallTP = 0;
      int overallPRED = 0;
      int overallANN = 0;

      for (File labeledFile : subFolder.listFiles()) {
        File testFile = new File(testFolder.getAbsolutePath() + "/" + labeledFile.getName());
        if (new File(testFolder.getAbsolutePath() + "/" + labeledFile.getName()).exists()) {
          String testContent = FileHelper.readFileAsString(testFile, Charset.forName("UTF-8"));
          String labeledContent =
              FileHelper.readFileAsString(labeledFile, Charset.forName("UTF-8"));
          String originalContent =
              labeledContent.replaceAll("<ENAMEX TYPE[^>]*>", "").replace("</ENAMEX>", "");

          Map<String[], String> testEntities = extractEntities(originalContent, testContent);
          Map<String[], String> annEntities = extractEntities(originalContent, labeledContent);

          for (String[] key : testEntities.keySet()) {
            if (key[2].equals("PERSON"))
              predPER++;
            if (key[2].equals("ORGANIZATION"))
              predORG++;
            if (key[2].equals("LOCATION"))
              predLOC++;
          }

          for (String[] key : annEntities.keySet()) {
            if (key[2].equals("PERSON"))
              annPER++;
            if (key[2].equals("ORGANIZATION"))
              annORG++;
            if (key[2].equals("LOCATION"))
              annLOC++;
          }

          for (String[] key1 : annEntities.keySet()) {

            for (String[] key2 : testEntities.keySet()) {
              if (key1[0].equals(key2[0]) && key1[1].equals(key2[1]) && key1[2].equals(key2[2])
                  && annEntities.get(key1).equals(testEntities.get(key2))
                  && key1[2].equals("PERSON")) {
                tpPER++;
                break;
              }

              if (key1[0].equals(key2[0]) && key1[1].equals(key2[1]) && key1[2].equals(key2[2])
                  && annEntities.get(key1).equals(testEntities.get(key2))
                  && key1[2].equals("ORGANIZATION")) {
                tpORG++;
                break;
              }

              if (key1[0].equals(key2[0]) && key1[1].equals(key2[1]) && key1[2].equals(key2[2])
                  && annEntities.get(key1).equals(testEntities.get(key2))
                  && key1[2].equals("LOCATION")) {
                tpLOC++;
                break;
              }
            }
          }
        } else
          System.err.println(testFile);
      }
      double PPER = tpPER / (double) predPER;
      double PORG = tpORG / (double) predORG;
      double PLOC = tpLOC / (double) predLOC;

      double RPER = tpPER / (double) annPER;
      double RORG = tpORG / (double) annORG;
      double RLOC = tpLOC / (double) annLOC;

      double FPER = 2 * PPER * RPER / (PPER + RPER);
      double FORG = 2 * PORG * RORG / (PORG + RORG);
      double FLOC = 2 * PLOC * RLOC / (PLOC + RLOC);

      overallTP = tpPER + tpORG + tpLOC;
      overallPRED = predPER + predORG + predLOC;
      overallANN = annPER + annORG + annLOC;
      double overallP = overallTP / (double) overallPRED;
      double overallR = overallTP / (double) overallANN;
      double overallF = 2 * overallP * overallR / (overallP + overallR);

      tpTotalPER += tpPER;
      tpTotalORG += tpORG;
      tpTotalLOC += tpLOC;
      predTotalPER += predPER;
      predTotalORG += predORG;
      predTotalLOC += predLOC;
      annTotalPER += annPER;
      annTotalORG += annORG;
      annTotalLOC += annLOC;
      overallTotalTP += overallTP;
      overallTotalPRED += overallPRED;
      overallTotalANN += overallANN;

      System.out.println("PERSON" + "\t\t" + tpPER + "\t" + predPER + "\t" + annPER + "\tP=" + PPER
          + "\tR=" + RPER + "\tF=" + FPER);
      System.out.println("ORGANIZATION" + "\t" + tpORG + "\t" + predORG + "\t" + annORG + "\tP="
          + PORG + "\tR=" + RORG + "\tF=" + FORG);
      System.out.println("LOCATION" + "\t" + tpLOC + "\t" + predLOC + "\t" + annLOC + "\tP=" + PLOC
          + "\tR=" + RLOC + "\tF=" + FLOC);
      System.out.println("OVERALL" + "\t\t" + overallTP + "\t" + overallPRED + "\t" + overallANN
          + "\tP=" + overallP + "\tR=" + overallR + "\tF=" + overallF);
    }

    double PPER = tpTotalPER / (double) predTotalPER;
    double PORG = tpTotalORG / (double) predTotalORG;
    double PLOC = tpTotalLOC / (double) predTotalLOC;

    double RPER = tpTotalPER / (double) annTotalPER;
    double RORG = tpTotalORG / (double) annTotalORG;
    double RLOC = tpTotalLOC / (double) annTotalLOC;

    double FPER = 2 * PPER * RPER / (PPER + RPER);
    double FORG = 2 * PORG * RORG / (PORG + RORG);
    double FLOC = 2 * PLOC * RLOC / (PLOC + RLOC);

    overallTotalTP = tpTotalPER + tpTotalORG + tpTotalLOC;
    overallTotalPRED = predTotalPER + predTotalORG + predTotalLOC;
    overallTotalANN = annTotalPER + annTotalORG + annTotalLOC;
    double overallP = overallTotalTP / (double) overallTotalPRED;
    double overallR = overallTotalTP / (double) overallTotalANN;
    double overallF = 2 * overallP * overallR / (overallP + overallR);

    System.out.println();
    System.out.println("-----------------------------");
    System.out.println("Total Evaluation");
    System.out.println("-----------------------------");

    System.out.println("PERSON" + "\t\t" + tpTotalPER + "\t" + predTotalPER + "\t" + annTotalPER
        + "\tP=" + PPER + "\tR=" + RPER + "\tF=" + FPER);
    System.out.println("ORGANIZATION" + "\t" + tpTotalORG + "\t" + predTotalORG + "\t" + annTotalORG
        + "\tP=" + PORG + "\tR=" + RORG + "\tF=" + FORG);
    System.out.println("LOCATION" + "\t" + tpTotalLOC + "\t" + predTotalLOC + "\t" + annTotalLOC
        + "\tP=" + PLOC + "\tR=" + RLOC + "\tF=" + FLOC);
    System.out.println("OVERALL" + "\t\t" + overallTotalTP + "\t" + overallTotalPRED + "\t"
        + overallTotalANN + "\tP=" + overallP + "\tR=" + overallR + "\tF=" + overallF);
  }

  public static Map<String[], String> extractEntities(String originalContent,
      String labeledContent) {
    Map<String[], String> entities = new HashMap<String[], String>();

    Map<Integer, String> labeledEntities =
        findStringRegex(labeledContent, "<ENAMEX TYPE[^>]*>([^<]*)</ENAMEX>");
    Map<Integer, String> labeledNestedEntities = findStringRegex(labeledContent,
        "<ENAMEX TYPE[^>]*>([^<]*<ENAMEX TYPE[^>]*>[^<]*</ENAMEX>[^<]*){1,}</ENAMEX>");
    Map<Integer, String> labeled2layerEntities = findStringRegex(labeledContent,
        "<ENAMEX TYPE[^>]*>([^<]*<ENAMEX TYPE[^>]*>[^<]*<ENAMEX TYPE[^>]*>[^<]*</ENAMEX>[^<]*</ENAMEX>[^<]*)</ENAMEX>");

    int idx = 0;
    for (Integer key : labeled2layerEntities.keySet()) {
      String entity = labeled2layerEntities.get(key).replaceAll("<ENAMEX TYPE[^>]*>", "")
          .replace("</ENAMEX>", "");

      String type = "";
      if (labeled2layerEntities.get(key).startsWith("<ENAMEX TYPE=\"PERSON\">"))
        type = "PERSON";
      if (labeled2layerEntities.get(key).startsWith("<ENAMEX TYPE=\"ORGANIZATION\">"))
        type = "ORGANIZATION";
      if (labeled2layerEntities.get(key).startsWith("<ENAMEX TYPE=\"LOCATION\">"))
        type = "LOCATION";
      if (labeled2layerEntities.get(key).startsWith("<ENAMEX TYPE=\"MISCELLANEOUS\">"))
        type = "MISCELLANEOUS";

      int be = originalContent.indexOf(entity, idx);
      int ee = be + entity.length();
      idx = ee;

      entities.put(new String[] {be + "", ee + "", type, "outer"}, entity);
    }

    idx = 0;
    for (Integer key : labeledNestedEntities.keySet()) {
      String entity = labeledNestedEntities.get(key).replaceAll("<ENAMEX TYPE[^>]*>", "")
          .replace("</ENAMEX>", "");

      String type = "";
      if (labeledNestedEntities.get(key).startsWith("<ENAMEX TYPE=\"PERSON\">"))
        type = "PERSON";
      if (labeledNestedEntities.get(key).startsWith("<ENAMEX TYPE=\"ORGANIZATION\">"))
        type = "ORGANIZATION";
      if (labeledNestedEntities.get(key).startsWith("<ENAMEX TYPE=\"LOCATION\">"))
        type = "LOCATION";
      if (labeledNestedEntities.get(key).startsWith("<ENAMEX TYPE=\"MISCELLANEOUS\">"))
        type = "MISCELLANEOUS";

      int be = originalContent.indexOf(entity, idx);
      int ee = be + entity.length();
      idx = ee;

      entities.put(new String[] {be + "", ee + "", type, "outer"}, entity);
    }

    idx = 0;
    for (Integer key : labeledEntities.keySet()) {
      String entity =
          labeledEntities.get(key).replaceAll("<ENAMEX TYPE[^>]*>", "").replace("</ENAMEX>", "");

      String type = "";
      if (labeledEntities.get(key).startsWith("<ENAMEX TYPE=\"PERSON\">"))
        type = "PERSON";
      if (labeledEntities.get(key).startsWith("<ENAMEX TYPE=\"ORGANIZATION\">"))
        type = "ORGANIZATION";
      if (labeledEntities.get(key).startsWith("<ENAMEX TYPE=\"LOCATION\">"))
        type = "LOCATION";
      if (labeledEntities.get(key).startsWith("<ENAMEX TYPE=\"MISCELLANEOUS\">"))
        type = "MISCELLANEOUS";

      int be = originalContent.indexOf(entity, idx);
      int ee = be + entity.length();
      idx = ee;

      entities.put(new String[] {be + "", ee + "", type, "outer"}, entity);
    }

    return entities;
  }

  public static void print(Map<String[], String> entities) {
    for (String[] key : entities.keySet())
      System.out.println(
          entities.get(key) + "\t" + key[2] + "\t" + key[0] + "\t" + key[1] + "\t" + key[3]);
  }

  public static Map<Integer, String> findStringRegex(String text, String rule) {
    Map<Integer, String> matchList = new TreeMap<Integer, String>();
    Pattern regex = Pattern.compile(rule, Pattern.DOTALL);
    Matcher regexMatcher = regex.matcher(text);
    while (regexMatcher.find()) {
      matchList.put(regexMatcher.start(), regexMatcher.group());
    }
    return matchList;
  }

}
